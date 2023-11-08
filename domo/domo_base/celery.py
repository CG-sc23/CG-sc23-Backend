from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "domo_base.settings")

app = Celery(
    "domo_base", broker="amqp://", backend="rpc://", include=["domo_api.tasks"]
)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.update(
    CELERYBEAT_SCHEDULE={
        "github-fail-check-every-30-minutes": {
            "task": "domo_api.tasks.periodic_fail_check_github_history",
            "schedule": crontab(minute="*/30"),
            "args": (),
        },
        "github-update-every-day": {
            "task": "domo_api.tasks.periodic_update_github_history",
            "schedule": crontab(minute=0, hour=15),
            "args": (),
        },
    }
)
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
