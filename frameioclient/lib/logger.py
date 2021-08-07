import logging


class SDKLogger:
    def __init__(self, log_name):
        self.initialize_logger()
        self.logger = logging.getLogger(log_name)

    def initialize_logger(self):
        logging.basicConfig(level=logging.INFO)

    def info(self, message):
        self.logger.info(message)
