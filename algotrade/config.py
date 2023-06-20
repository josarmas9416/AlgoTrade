import logging
import configparser

class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("algotrader.conf")

        log_level = self.config.get("global", "log_level")

        if log_level == "debug":
            log_level = logging.DEBUG
        elif log_level == "info":
            log_level = logging.INFO
        elif log_level == "warn":
            log_level = logging.WARNING
        elif log_level == "error":
            log_level = logging.ERROR
        elif log_level == "critical":
            log_level = logging.CRITICAL
        else:
            log_level = logging.WARNING

        logging.basicConfig(level=log_level)



    def get_account(self):
        return self.config.getint('mt5', 'account')

    def get_password(self):
        return self.config.get('mt5', 'password')

    def get_server(self):
        return self.config.get('mt5', 'server')

    def get_path(self):
        return self.config.get('mt5', 'path')
    