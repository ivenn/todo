import os
from app import app

log_path = app.config['LOGS_FILE_PATH']
if not os.path.isdir(log_path):
    os.makedirs(log_path)

LOGGER = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "%(asctime)s [%(threadName)-8.8s] [%(levelname)-3.3s] %(name)s: "
                          "%(message)s [in %(filename)s:%(lineno)d]"
            }
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "verbose",
                "stream": "ext://sys.stdout"
            },

            "basic_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "verbose",
                "filename": str(log_path) + "todolist.log",
                "maxBytes": 1024*1024*1024,
                "backupCount": 5,
                "encoding": "utf8"
            },

        },

        "loggers": {
            "sqlalchemy": {
                "level": "ERROR",
                "handlers": ["basic_file_handler"],
            }
        },

        "root": {
            "level": "DEBUG",
            "handlers": ["basic_file_handler", "console"]
        }
}

LOGGERS_FOR_USE = {"LOGGER": LOGGER}