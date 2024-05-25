from celery.schedules import crontab

from combo_investment import settings

beat_schedules = {
    "update_all_securities_prices_everyday_at_10AM": {
        "task": "datahub.tasks.update_all_securities_prices",
        "schedule": crontab(minute=0, hour=10),  # every day at 10 AM
        "options": {"queue": settings.SCHEDULED_TASK_QUEUE},
    },
    "update_all_securities_prices_everyday_at_5PM": {
        "task": "datahub.tasks.update_all_securities_prices",
        "schedule": crontab(minute=0, hour=17),  # every day at 5 PM
        "options": {"queue": settings.SCHEDULED_TASK_QUEUE},
    },
    # "run_every_1_hour": {
    #     "task": "datahub.tasks.update_all_securities_prices",
    #     "schedule": crontab(minute=0),
    # },
}
