import os.path
from config import log_dir

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
                "filename": os.path.join(log_dir, 'todo.log'),
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

LOGGERS = {"LOGGER": LOGGER}