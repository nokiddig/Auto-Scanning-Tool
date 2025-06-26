import logging
from datetime import datetime

logging.basicConfig(
        encoding="utf-8",
        level=logging.INFO
    )

# Get logger with name and set log level, handler and formatter
# log file will be created in log folder with date as filename
# name: logger prefix
def get_logger(name):
    today = datetime.today().date()

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Create file handler
    file_handler = logging.FileHandler(f'../output/log/{today}.log')
    file_handler.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)6s - %(name)7s - %(message)s')

    # Set default value for 'name' in extra
    record = logging.makeLogRecord({'name': 'default_name'})
    formatter.format(record)
    file_handler.setFormatter(formatter)

    # Remove existing handlers add handler to current logger
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
    logger.addHandler(file_handler)

    return logger