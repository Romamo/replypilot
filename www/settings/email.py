from .env import env

SERVER_EMAIL = 'info@appstorespy.com'
DEFAULT_FROM_EMAIL = "Appstorespy <{}>".format(SERVER_EMAIL)
EMAIL_REPLY_TO = 'info@appstorespy.com'
EMAIL_CONFIG = env.email_url('EMAIL_URL')
if EMAIL_CONFIG:
    vars().update(EMAIL_CONFIG)
