import logging, logging.config, logging.handlers

logging.config.fileConfig('config/logging.conf')

root = logging.getLogger()
file_handler = next((h for h in root.handlers if isinstance(h, logging.FileHandler)), None)
buffer_handler = next((h for h in root.handlers if isinstance(h, logging.handlers.MemoryHandler)), None)

if buffer_handler and file_handler:
    buffer_handler.setTarget(file_handler)


def init_logger(name):
    logger = logging.getLogger(name)
    return logger
    