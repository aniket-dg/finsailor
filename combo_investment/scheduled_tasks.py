from celery.schedules import crontab

from combo_investment import settings

beat_schedules = {
    "update_all_securities_prices_everyday_at_10AM": {
        "task": "datahub.tasks.calculate_security_prices_sector_performance",
        "schedule": crontab(minute="0", hour="10"),  # every day at 10 AM
        "options": {"queue": settings.SCHEDULED_TASK_QUEUE},
    },
    "update_all_securities_prices_everyday_at_5PM": {
        "task": "datahub.tasks.calculate_security_prices_sector_performance",
        "schedule": crontab(minute="0", hour="17"),  # every day at 5 PM
        "options": {"queue": settings.SCHEDULED_TASK_QUEUE},
    },
    "update_stock_indices_from_nse_at_4PM": {
        "task": "datahub.tasks.update_stock_indices_from_nse",
        "schedule": crontab(minute="0", hour="16"),  # every day at 4 PM
        "options": {"queue": settings.SCHEDULED_TASK_QUEUE},
    }
    # "run_every_1_hour": {
    #     "task": "datahub.tasks.update_all_securities_prices",
    #     "schedule": crontab(minute=0),
    # },
}
