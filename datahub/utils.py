from django.db.models import Sum, F

from datahub.models import GeneralInfo, Security


def get_general_info_obj():
    general_info = GeneralInfo.objects.last()
    return GeneralInfo() if general_info is None else general_info


def get_all_securities():
    return Security.objects.filter(security_info__tradingStatus="Active")


def get_industry_index(index_type_id: int, date: str, index_type="macro_sector"):
    securities = Security.select_related.with_close_price(date).filter(
        last_price__isnull=False
    )
    if index_type == "basic_industry":
        securities = securities.filter(basic_industry_id=index_type_id)
    elif index_type == "industry":
        securities = securities.filter(basic_industry__industry_id=index_type_id)
    elif index_type == "sector":
        securities = securities.filter(
            basic_industry__industry__sector_id=index_type_id
        )
    else:
        securities = securities.filter(
            basic_industry__industry__sector__macro_sector_id=index_type_id
        )

    total_market_cap = securities.aggregate(total=Sum("market_cap"))["total"]
    total_free_float_cap = securities.aggregate(total=Sum("free_float_market_cap"))[
        "total"
    ]

    index_value_market_cap = 0
    index_value_free_float_cap = 0
    for security in securities:
        weight = float(security["market_cap"] / total_market_cap)
        free_float_weight = float(
            security["free_float_market_cap"] / total_free_float_cap
        )
        weighted_price = weight * float(security["last_price"])
        free_float_weighted_price = free_float_weight * float(security["last_price"])
        index_value_market_cap += weighted_price
        index_value_free_float_cap += free_float_weighted_price

    return index_value_market_cap, index_value_free_float_cap
