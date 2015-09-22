import os
import logging

from logging.handlers import RotatingFileHandler
from app import app

logging.basicConfig()

class LoggingUtils(object):
    file_handler = None
    default_logs_level = app.config['DEFAULT_LOGS_LEVEL']

    @staticmethod
    def initialize_logging():
        """
        Set up initial logging parameters

        :return: None
        """
        if not LoggingUtils.file_handler:
            log_path = app.config['LOGS_FILE_PATH']
            if not os.path.isdir(log_path):
                os.makedirs(log_path)
            LoggingUtils.file_handler = file_handler = RotatingFileHandler(
                log_path + 'todolist.log', mode='a', maxBytes=1024*1024*1024, backupCount=5)
            if not app.debug:
                file_handler.setLevel(logging.INFO)
            else:
                file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s [%(threadName)-8.8s] [%(levelname)-3.3s] %(name)s: %(message)s [in %(filename)s:%(lineno)d]'))
            app.logger.addHandler(file_handler)
            app.logger.setLevel(LoggingUtils.default_logs_level)
            app.logger.info('ToDOoist startup')
            app.logger.info('Default log level is \'%s\'' % (LoggingUtils.default_logs_level,))
            LoggingUtils.new_logger_registration('sqlalchemy', logging.ERROR)
        else:
            app.logger.info("initialize_logging was called not in first time")

    @staticmethod
    def new_logger_registration(logger_name, level=default_logs_level):
        """
        get logger and add app file handler for this logger

        :param logger_name: name of new logger
        :param level: default log level

        :return: New logger
        """
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        if LoggingUtils.file_handler:
            logger.addHandler(LoggingUtils.file_handler)
        return logger

