from celery import shared_task

from combo_investment.celery import BaseTaskWithRetry
from groww.views import GrowwInvestment
from mutual_funds.models import FundInvestment
from users.models import User


@shared_task(base=BaseTaskWithRetry)
def update_fund_investment_transactions(user_id):
    fund_investments = FundInvestment.objects.filter(user_id=user_id)
    user = User.objects.filter(id=user_id).last()
    groww_investment = GrowwInvestment(user=user)
    for investment in fund_investments:
        groww_investment.process_fund_transactions(investment)
