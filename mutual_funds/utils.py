import datetime
from typing import List

from datahub.models import Security
from mutual_funds.models import FundSecurity, Fund
from mutual_funds.views import MutualFund


def create_fund_securities(fund: Fund, securities: List[dict]):
    mutual_fund = MutualFund()
    fund.holdings.all().delete()
    for security in securities:
        sec = mutual_fund.get_or_create_security(security["company_name"])
        portfolio_date = datetime.datetime.strptime(security["portfolio_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        fund_security = FundSecurity(
            security_id=sec.id,
            fund_id=fund.id,
            portfolio_date=portfolio_date,
            nature_name=security.get("nature_name"),
            market_value=security.get("market_value"),
            corpus_per=security.get("corpus_per"),
            market_cap=security.get("market_cap"),
            rating_market_cap=security.get("rating_market_cap"),
            scheme_code=security.get("scheme_code"),
        )
        fund_security.save()
