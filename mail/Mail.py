# %%
import importlib.util
import os
module_internal_path = os.path.join(os.getcwd(), '..', 'internal', 'variable.py')
spec = importlib.util.spec_from_file_location("variable", module_internal_path)
module_internal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module_internal)

MAILER_SENDER_SINGLEID = 'SecurityToolSystem'
MAILER_SENDER_PASSWORD = module_internal.PASSWORD

with open('../common/logger.py') as f:
    exec(f.read())

logger = get_logger(name='mail')

# %%
import smtplib
import sqlite3 as lite
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from config import *

from datetime import datetime

# %%
RECIPIENT_FROM_CONFIG = 0
RECIPIENT_FROM_DATABASE = 1
RECIPIENT_ONLY_MAINTAINERS = 2
MAIL_PREFIX = 'SAT'
MAILLIST_TO = ['vansy.le@samsung.com', 'thuy.ptt@samsung.com']# 'huy.nq2@samsung.com']
MAILLIST_CC = []
MONITOR_MAINTAINER_MAILLIST = []
IGNORE_MALWARE = [
    "not-a-malware-app",
    "safe-app",
    "trusted-app"
]

# %%
# Mail content
today = datetime.today().date()
file_path = f'../output/output_{today}.xlsx'

str_today = today.strftime('%Y.%m.%d')
MAIL_SUBJECT = f'Auto Scanning Result of {str_today}'
MAIL_BODY = 'Hello!\nThis is an automated email sent by system about new KG unlock case reported in this week. Please check the attachment for detail!\nThank you.'
ATTACHMENT = [file_path]

# %%
class Mail:
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

# %%
try:
    mail = Mail()
    mail.setTo(MAILLIST_TO)
    mail.setCc(MAILLIST_CC)
    mail.setSubject(MAIL_SUBJECT)
    mail.setBody(MAIL_BODY)
    mail.setAttachment(ATTACHMENT)
    mail.sendMail()
    logger.info('Mail sent successful')
except Exception as e:
    print(e)
    logger.error(e)


