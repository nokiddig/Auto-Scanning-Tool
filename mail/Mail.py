# ==========================================================
# ======================== Import ==========================
# ==========================================================

import os
import smtplib
import sqlite3 as lite
import importlib.util
from config import *
from datetime import datetime
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

# Run file logger.py to create logger object with prefix 'mail'
with open('../common/logger.py') as f:
    exec(f.read())
logger = get_logger(name='mail')


# Import a module from another directory
def get_module(folder_name, file_name):
    module_name = file_name.split('.')[0]
    module_path = os.path.join(os.getcwd(), '..', folder_name, file_name)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# ==========================================================
# ======================= Init data ========================
# ==========================================================

# From input import sender, receiver, subject,...
input_module = get_module('internal', 'mail_input.py')
MAILER_SENDER_SINGLEID = input_module.MAILER_SENDER_SINGLEID
MAILER_SENDER_PASSWORD = input_module.MAILER_SENDER_PASSWORD
MAILLIST_TO = input_module.MAILLIST_TO
MAILLIST_CC = input_module.MAILLIST_CC
MAIL_PREFIX = input_module.MAIL_PREFIX


RECIPIENT_FROM_CONFIG = 0
RECIPIENT_FROM_DATABASE = 1
RECIPIENT_ONLY_MAINTAINERS = 2
MONITOR_MAINTAINER_MAILLIST = []
IGNORE_MALWARE = [
    "not-a-malware-app",
    "safe-app",
    "trusted-app"
]


# Init mail content.
MAIL_SUBJECT = input_module.MAIL_SUBJECT
MAIL_BODY = input_module.MAIL_BODY
ATTACHMENT = input_module.ATTACHMENT

# ==========================================================
# ======================== Mail ============================
# ==========================================================

class Mail:
    # Init mail object and set sender, smtp server and port.
    def __init__(self):
        self.message = MIMEMultipart()
        self.smtp_server = "smtpsys.samsung.net"
        self.smtp_port = 25
        self.sender = f"{MAILER_SENDER_SINGLEID}@samsung.com"
        self.message["From"] = self.sender
        self.receivers = []
        self.attachments = []
        self.readyToSend = True

    def setBody(self, body: str, type: str = "plain"):
        self.message.attach(MIMEText(_text=body, _subtype=type, _charset="utf-8"))
        return self

    def setCc(self, receivers: list[str]):
        self.message["Cc"] = ", ".join(receivers)
        self.addReceivers(receivers)
        return self

    def setTo(self, receivers: list[str]):
        self.message["To"] = ", ".join(receivers)
        self.addReceivers(receivers)
        return self

    def setSubject(self, subject: str):
        self.message["Subject"] = f"[{MAIL_PREFIX}] {subject}"
        return self

    def setReceivers(self, receivers: list[str]):
        self.receivers = receivers
        return self

    def addReceivers(self, receivers: list[str]):
        self.receivers.extend(receivers)
        return self

    # Add attachments to mail.
    # Attachments should be a list of file paths.
    def setAttachment(self, attachment: list[str]):
        self.attachments = attachment
        for _path in self.attachments:
            name = _path.replace("\\", "/").split("/")[-1]
            with open(_path, "rb") as attach:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attach.read())
                part.add_header("Content-Disposition", "attachment", filename=name)
                encoders.encode_base64(part)
                self.message.attach(part)
        return self

    def default(self, type: int = RECIPIENT_FROM_CONFIG):
        """
        Set recipients using the list contained in the database or config.py file or maintainers.

        type:
            0: from config file
            1: from database
            2: only maintainers
        """
        to = []
        cc = []
        if type == RECIPIENT_FROM_DATABASE:
            con = lite.connect(db)
            cur = con.cursor()
            res = cur.execute("select * from AVTool_member")
            for row in res:
                _id, email, receipt, status = row
                if status == 1:
                    if receipt == 0:
                        to.append(email)
                    elif receipt == 1:
                        cc.append(email)
        elif type == RECIPIENT_FROM_CONFIG:
            to = MAILLIST_TO
            cc = MAILLIST_CC
        elif type == RECIPIENT_ONLY_MAINTAINERS:
            to = MONITOR_MAINTAINER_MAILLIST
        self.setTo(to)
        self.setCc(cc)
        return self

    def sendMail(self):
        if not self.readyToSend:
            return
        with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=60) as sv:
            sv.ehlo()
            # sv.login(self.sender, self.pwd)
            sv.sendmail(self.sender, self.receivers, self.message.as_string())


# Send mail to all members and CC to those who want to receive it.
try:
    mail = Mail()
    mail.setTo(MAILLIST_TO)
    mail.setCc(MAILLIST_CC)
    mail.setSubject(MAIL_SUBJECT)
    mail.setBody(MAIL_BODY)
    mail.setAttachment(ATTACHMENT)
    mail.sendMail()
    logger.info('Mail was sent successfully')
except Exception as e:
    logger.error(f"Fail to send mail: {e}")
