import logging
from logging.config import dictConfig

#loging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        },
        "detailed": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s]: [%(filename)s:%(lineno)d]: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "detailed",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}

#apply your settings
def setup_logging():
    dictConfig(LOGGING_CONFIG)
