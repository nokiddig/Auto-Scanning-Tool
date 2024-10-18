import logging
from datetime import datetime

def get_logger(name):
    today = datetime.today().date()

    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # create file handler
    file_handler = logging.FileHandler(f'../log/{today}.log')
    file_handler.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)6s - %(name)7s - %(message)s')

    # set default value for 'name' in extra
    record = logging.makeLogRecord({'name': 'default_name'})
    formatter.format(record)

    file_handler.setFormatter(formatter)

    # add handler to logger
    for handler in logger.handlers[:]:  # clear other logger
        logger.removeHandler(handler)
        handler.close()
    logger.addHandler(file_handler)

    return logger