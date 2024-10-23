from .apps import *
from .django import *
from .logging import *
from .email import *

if DEBUG_DB:
    LOGGING['loggers']['django.db.backends']['level'] = 'DEBUG'
