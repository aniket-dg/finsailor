import datetime
from typing import List

from datahub.models import Security
from mutual_funds.models import FundSecurity, Fund
from scrapper.views import NSEScrapper
from datahub.tasks import update_security_price


def get_or_create_security(name, base_security=True):
    nse = NSEScrapper()
    symbol = nse.get_symbol(name)
    security, created = Security.objects.get_or_create(
        symbol=symbol, defaults={"name": name, "base_security": base_security}
    )
    if created:
        update_security_price.delay(security.id)
    return security


def create_fund_securities(fund: Fund, securities: List[dict]):
    fund.holdings.all().delete()
    for security in securities:
        sec = get_or_create_security(security["company_name"], base_security=False)
        portfolio_date = datetime.datetime.strptime(
            security["portfolio_date"], "%Y-%m-%dT%H:%M:%S.%fZ"
        )
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
