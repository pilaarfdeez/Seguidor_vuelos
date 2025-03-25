import logging
import logging.config

logging.config.fileConfig('config/logging.conf')

def init_logger(name):
    logger = logging.getLogger(name)
    return logger
    