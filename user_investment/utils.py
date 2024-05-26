import datetime
import logging
from _decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
from zoneinfo import ZoneInfo

from django.db.models import Sum, DecimalField
from django.db.models.functions import Cast

from combo_investment import settings
from combo_investment.settings import TIME_ZONE
from combo_investment.utils import is_market_close_today
from datahub.models import Security, Parameter
from datahub.serializers import (
    SecuritySerializer,
    SecuritySerializerForSectorWisePortfolio,
)
from industries.models import MacroSector, Sector, Industry, BasicIndustry
from django.db import models

from datetime import date, timedelta
from django.db.models import Count, F, Sum

logger = logging.Logger("UserInvestment - Utils")


def get_securities_by_sector(investments, show_zero_allocation_sectors=True):
    sector_wise_portfolio = {
        "basic_industry": {},
        "industry": {},
        "sector": {},
        "macro_sector": {},
    }
    metadata = {
        "no_of_stocks": investments.aggregate(total_quantity=Sum("quantity"))[
            "total_quantity"
        ],
        "allocation": 100,
    }

    if show_zero_allocation_sectors:
        macro_sectors = MacroSector.objects.all()
        sectors = Sector.objects.all()
        industries = Industry.objects.all()
        basic_industries = BasicIndustry.objects.all()
    else:
        macro_sector_ids = investments.values_list(
            "security__basic_industry__industry__sector__macro_sector__id", flat=True
        )
        macro_sectors = MacroSector.objects.filter(id__in=macro_sector_ids)
        sector_ids = investments.values_list(
            "security__basic_industry__industry__sector__id", flat=True
        )
        sectors = Sector.objects.filter(id__in=sector_ids)
        industries_ids = investments.values_list(
            "security__basic_industry__industry__id", flat=True
        )
        industries = Industry.objects.filter(id__in=industries_ids)
        basic_industries_ids = investments.values_list(
            "security__basic_industry__id", flat=True
        )
        basic_industries = BasicIndustry.objects.filter(id__in=basic_industries_ids)

    sectors_investments = investments.filter(
        security__basic_industry__industry__sector__macro_sector__id__in=macro_sectors.values_list(
            "id", flat=True
        )
    )
    macro_sectors_total_securities = sectors_investments.aggregate(
        total_quantity=Sum("quantity")
    )["total_quantity"]
    macro_sector_data = {
        "metadata": {
            "no_of_stocks": macro_sectors_total_securities,
            "allocation": (
                round(
                    ((macro_sectors_total_securities / metadata["no_of_stocks"]) * 100),
                    2,
                )
                if metadata["no_of_stocks"] > 0
                else 100
            ),
        },
        "data": get_macro_sector_allocation(
            macro_sectors_total_securities, macro_sectors, sectors_investments
        ),
    }

    sector_wise_portfolio["macro_sector"] = macro_sector_data

    sectors_investments = investments.filter(
        security__basic_industry__industry__sector__id__in=sectors.values_list(
            "id", flat=True
        )
    )
    sectors_total_securities = sectors_investments.aggregate(
        total_quantity=Sum("quantity")
    )["total_quantity"]
    sector_data = {
        "metadata": {
            "no_of_stocks": sectors_total_securities,
            "allocation": (
                round(((sectors_total_securities / metadata["no_of_stocks"]) * 100), 2)
                if metadata["no_of_stocks"] > 0
                else 100
            ),
        },
        "data": get_sector_allocation(
            sectors_total_securities, sectors, sectors_investments
        ),
    }

    sector_wise_portfolio["sector"] = sector_data

    industries_investments = investments.filter(
        security__basic_industry__industry__id__in=industries.values_list(
            "id", flat=True
        )
    )
    industries_total_securities = industries_investments.aggregate(
        total_quantity=Sum("quantity")
    )["total_quantity"]
    industries_data = {
        "metadata": {
            "no_of_stocks": industries_total_securities,
            "allocation": (
                round(
                    ((industries_total_securities / metadata["no_of_stocks"]) * 100), 2
                )
                if metadata["no_of_stocks"] > 0
                else 100
            ),
        },
        "data": get_industry_allocation(
            industries_total_securities, industries, industries_investments
        ),
    }

    sector_wise_portfolio["industry"] = industries_data

    basic_industries_investments = investments.filter(
        security__basic_industry__id__in=basic_industries.values_list("id", flat=True)
    )
    basic_industries_total_securities = basic_industries_investments.aggregate(
        total_quantity=Sum("quantity")
    )["total_quantity"]
    basic_industries_data = {
        "metadata": {
            "no_of_stocks": basic_industries_total_securities,
            "allocation": (
                round(
                    (
                        (basic_industries_total_securities / metadata["no_of_stocks"])
                        * 100
                    ),
                    2,
                )
                if metadata["no_of_stocks"] > 0
                else 100
            ),
        },
        "data": get_basic_industry_allocation(
            basic_industries_total_securities,
            basic_industries,
            basic_industries_investments,
        ),
    }

    sector_wise_portfolio["basic_industry"] = basic_industries_data

    return {"data": sector_wise_portfolio, "metadata": metadata}


def get_macro_sector_allocation(
    total_securities, macro_sectors, macro_sectors_investments
):
    macro_sector_allocation = {}
    for macro_sector in macro_sectors:
        res = {}
        metadata = {"details": None}
        macro_sector_investments = macro_sectors_investments.filter(
            security__basic_industry__industry__sector__macro_sector__name=macro_sector.name
        )
        metadata["no_of_stocks"] = (
            macro_sector_investments.aggregate(total_quantity=Sum("quantity"))[
                "total_quantity"
            ]
            or 0
        )

        sector_allocation = (
            round(((metadata["no_of_stocks"] / total_securities) * 100), 2)
            if total_securities > 0
            else 100
        )
        metadata["allocation"] = sector_allocation
        securities = get_security_allocation(
            metadata["no_of_stocks"], macro_sector_investments
        )
        amount_invested = sum(
            security["metadata"]["amount_invested"] for security in securities
        )
        metadata["amount_invested"] = amount_invested
        res["securities"] = securities
        macro_sector_allocation[macro_sector.name] = {"data": res, "metadata": metadata}

    return macro_sector_allocation


def get_sector_allocation(total_securities, sectors, sectors_investments):
    sector_allocation = {}
    for sector in sectors:
        res = {}
        metadata = {"details": None}
        sector_investments = sectors_investments.filter(
            security__basic_industry__industry__sector__name=sector.name
        )
        metadata["no_of_stocks"] = (
            sector_investments.aggregate(total_quantity=Sum("quantity"))[
                "total_quantity"
            ]
            or 0
        )

        allocation = (
            round(((metadata["no_of_stocks"] / total_securities) * 100), 2)
            if total_securities > 0
            else 100
        )
        metadata["allocation"] = allocation
        securities = get_security_allocation(
            metadata["no_of_stocks"], sector_investments
        )

        amount_invested = sum(
            security["metadata"]["amount_invested"] for security in securities
        )
        metadata["amount_invested"] = amount_invested
        res["securities"] = securities
        sector_allocation[sector.name] = {"data": res, "metadata": metadata}

    return sector_allocation


def get_industry_allocation(total_securities, industries, industries_investments):
    industries_allocation = {}
    for industry in industries:
        res = {}
        metadata = {"details": None}
        industry_investments = industries_investments.filter(
            security__basic_industry__industry__name=industry.name
        )
        metadata["no_of_stocks"] = (
            industry_investments.aggregate(total_quantity=Sum("quantity"))[
                "total_quantity"
            ]
            or 0
        )

        allocation = (
            round(((metadata["no_of_stocks"] / total_securities) * 100), 2)
            if total_securities > 0
            else 100
        )
        metadata["allocation"] = allocation
        securities = get_security_allocation(
            metadata["no_of_stocks"], industry_investments
        )
        amount_invested = sum(
            security["metadata"]["amount_invested"] for security in securities
        )
        metadata["amount_invested"] = amount_invested
        res["securities"] = securities
        industries_allocation[industry.name] = {"data": res, "metadata": metadata}

    return industries_allocation


def get_basic_industry_allocation(
    total_securities, basic_industries, basic_industries_investments
):
    basic_industries_allocation = {}
    for basic_industry in basic_industries:
        res = {}
        metadata = {"details": basic_industry.details}
        basic_industry_investments = basic_industries_investments.filter(
            security__basic_industry__name=basic_industry.name
        )
        metadata["no_of_stocks"] = (
            basic_industry_investments.aggregate(total_quantity=Sum("quantity"))[
                "total_quantity"
            ]
            or 0
        )

        allocation = (
            round(((metadata["no_of_stocks"] / total_securities) * 100), 2)
            if total_securities > 0
            else 100
        )
        metadata["allocation"] = allocation
        securities = get_security_allocation(
            metadata["no_of_stocks"], basic_industry_investments
        )
        amount_invested = sum(
            security["metadata"]["amount_invested"] for security in securities
        )
        metadata["amount_invested"] = amount_invested
        res["securities"] = securities
        basic_industries_allocation[basic_industry.name] = {
            "data": res,
            "metadata": metadata,
        }

    return basic_industries_allocation


def get_security_allocation(total_securities, investments):
    securities = []
    for investment in investments:
        security_data = {
            "security": SecuritySerializerForSectorWisePortfolio(
                investment.security, context={"broker": investment.broker}
            ).data,
            "metadata": {
                "no_of_stocks": investment.quantity,
                "allocation": (
                    round(((investment.quantity / total_securities) * 100), 2)
                    if total_securities > 0
                    else 100
                ),
                "amount_invested": round(investment.quantity * investment.avg_price, 2),
            },
        }
        securities.append(security_data)

    return securities


def get_security_percentage_change(investment):
    security = investment.security
    market_close_value_time = Parameter.objects.filter(name="CLOSE_PRICE_TIME").last()

    local_tz = ZoneInfo(settings.TIME_ZONE)
    today = datetime.datetime.now().astimezone(local_tz)
    today_data = security.historical_price_info.get(today.date().isoformat())

    if is_market_close_today():
        today_data = None

    if today_data is None:
        last_date = sorted(security.historical_price_info.keys())[-1]
        today_data = security.historical_price_info.get(last_date)

    last_price = Decimal(today_data.get("lastPrice"))
    if today.time() < market_close_value_time.time:
        last_price = Decimal(today_data.get("close"))

    last_close = Decimal(today_data.get("previousClose"))

    change = ((last_price - last_close) / last_close) * 100
    total_change = today_data.get("change") * investment.quantity

    res = {
        "p_change": change.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "change": Decimal(today_data.get("change")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        ),
        "total_change": Decimal(total_change).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        ),
    }

    return res


def calculate_todays_performance_by_macro_sector(securities):
    security = Security.objects.filter(symbol__in=["SJVN", "IRB", "SAIL", "PNB"]).last()
    macro_sectors = MacroSector.objects.all()
    macro_sector_name_to_securities = {}

    local_tz = ZoneInfo(TIME_ZONE)
    today_date = datetime.datetime.now().astimezone(local_tz).date()
    yesterday_date = (today_date - timedelta(days=1)).isoformat()
    if is_market_close_today():
        sorted_data = sorted(security.historical_price_info.keys())
        today_date = sorted_data[-1]
        yesterday_date = sorted_data[-2]
    for macro_sector in macro_sectors:
        macro_sector_securities = securities.filter(
            basic_industry__industry__sector__macro_sector_id=macro_sector.id
        )
        yesterdays_prices = []
        todays_prices = []

        for security in macro_sector_securities:
            logger.warning(security.id, security.symbol)
            yesterdays_data = security.historical_price_info.get(yesterday_date)
            yesterdays_price = (
                yesterdays_data["close"]
                if yesterdays_data["close"]
                else yesterdays_data["lastPrice"]
            )

            yesterdays_prices.append(yesterdays_price)
            todays_prices.append(float(security.last_updated_price))

        macro_sector_name_to_securities[macro_sector.name] = {
            "yesterdays_prices": yesterdays_prices,
            "todays_prices": todays_prices,
        }

    res = {}
    for macro_sector, macro_sector_data in macro_sector_name_to_securities.items():
        yesterdays_prices = macro_sector_data.pop("yesterdays_prices")
        todays_prices = macro_sector_data.pop("todays_prices")
        diff = sum(todays_prices) - sum(yesterdays_prices)
        res[macro_sector] = {
            "p_change": Decimal((diff / sum(yesterdays_prices)) * 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
            "change": diff,
        }

    res["date"] = today_date.strftime("%d %B %Y")
    return res
