from celery import shared_task

from combo_investment.celery import BaseTaskWithRetry
from datahub.models import Security
from user_investment.utils import calculate_todays_performance_by_macro_sector


@shared_task(base=BaseTaskWithRetry)
def calculate_todays_performance():
    calculate_todays_performance_by_macro_sector()
