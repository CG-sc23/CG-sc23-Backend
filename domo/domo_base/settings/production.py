# Sentry
import sentry_sdk
from django.core.exceptions import DisallowedHost

from .base import *


def before_send(event, hint):
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]
        if isinstance(exc_value, DisallowedHost):
            return None
    return event


sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    before_send=before_send,
)

DEBUG = False
ALLOWED_HOSTS = ["api.domowebest.com", "10.0.11.57"]

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
