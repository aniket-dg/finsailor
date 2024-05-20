from celery import shared_task

from combo_investment.celery import BaseTaskWithRetry
from mutual_funds.views import MutualFund, MutualFundInvestment


@shared_task(base=BaseTaskWithRetry)
def update_mutual_fund_books():
    mutual_fund_investment = MutualFundInvestment()
    mutual_fund_investment.process_mf_books()
