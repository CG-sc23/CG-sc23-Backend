# Sentry
import sentry_sdk

from .base import *

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)
DEBUG = False
ALLOWED_HOSTS = ["api.domowebest.com", "10.0.11.57"]
