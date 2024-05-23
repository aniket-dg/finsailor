import os

import django
from celery import Celery, Task
from combo_investment.scheduled_tasks import beat_schedules

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "combo_investment.settings")

app = Celery("combo_investment")
packages_with_tasks = [
    "dashboard",
    "data_import",
    "datahub",
    "industries",
    "scrapper",
    "user_investment",
    "users",
]

app.config_from_object("django.conf:settings", namespace="CELERY")

django.setup()
# Load task modules from all registered Django apps.
app.autodiscover_tasks(packages_with_tasks)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")


class BaseTaskWithRetry(Task):
    autoretry_for = (Exception,)
    max_retries = 2
    retry_backoff = 30
    retry_backoff_max = 700
    retry_jitter = False  # introduces randomness into retry backoff delays.


for name, schedule in beat_schedules.items():
    app.conf.beat_schedule[name] = schedule
