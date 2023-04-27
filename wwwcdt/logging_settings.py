#! /usr/bin/python2.7
import os
import logging
import sys

DOCKER_LOGGING = {
    "version": 1,
    # see django docs on it - setting it to True will NOT really disable loggers
    "disable_existing_loggers": False,

    "handlers": {
        "stdout": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "stream": sys.stdout
        },
    },
    "loggers": {
        # as found, it disables existing django loggers
        "django": {},

        "": { # default logger for any source
            "level": "WARNING",
            "handlers": ["stdout"],
        },
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": sys.stdout
        },
    },
    "loggers": {
        "django": {},
        "": {
            "level": "DEBUG",
            "handlers": ["console"],
        }
    }
}
