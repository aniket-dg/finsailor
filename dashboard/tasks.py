from celery import shared_task

from combo_investment.celery import BaseTaskWithRetry


@shared_task(base=BaseTaskWithRetry)
def dummy():
    print("dummy method called")
