import logging

from celery import shared_task

from combo_investment.celery import BaseTaskWithRetry
from groww.views import GrowwRequest

logger = logging.getLogger("Groww")


@shared_task(base=BaseTaskWithRetry)
def create_or_update_groww_fund(search_id):
    groww_request = GrowwRequest()
    groww_request.create_or_update_fund(search_id)
