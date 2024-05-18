import logging

from django.db.models import Sum

from datahub.models import Security
from datahub.serializers import (
    SecuritySerializer,
    SecuritySerializerForSectorWisePortfolio,
)
from industries.models import MacroSector, Sector, Industry, BasicIndustry

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
                investment.security
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
