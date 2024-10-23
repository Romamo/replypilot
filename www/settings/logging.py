import os

from .env import env


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format':
            '%(asctime)s %(levelname)s %(name)s %(module)s %(message)s',
            'datefmt': "%Y-%m-%dT%H:%M:%S"
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        },
        # 'json': {
        #     '()': 'json_log_formatter.JSONFormatter',
        # },
    },
    'filters': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'data/debug.log',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'main': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': 'data/logs/main.log',
            'maxBytes': 1024000,
            'backupCount': 3,
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            #            'formatter': 'simple'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['main', 'console'],  # 'mail_admins',
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
        },
        'elastic_transport.transport': {
            'level': 'ERROR',
            'handlers': ['console'],
        },
    }
}
