from datahub.models import Security
from datahub.serializers import (
    SecuritySerializer,
    SecuritySerializerForSectorWisePortfolio,
)


# def get_securities_by_sector(investments):
#     total_securities = sum(investments.values_list("quantity", flat=True))
#     sector_wise_portfolio = {
#         "basic_industry": {},
#         "industry": {},
#         "sector": {},
#         "macro_sector": {},
#     }
#     for portfolio_sector, res in sector_wise_portfolio.items():
#         distinuguish_by = portfolio_sector
#         sector_portfolio = res
#         for investment in investments:
#             security = investment.security
#             if distinuguish_by == "basic_industry":
#                 macro_sector = security.basic_industry.name
#             elif distinuguish_by == "industry":
#                 macro_sector = security.basic_industry.industry.name
#             elif distinuguish_by == "sector":
#                 macro_sector = security.basic_industry.industry.sector.name
#             else:
#                 macro_sector = security.basic_industry.industry.sector.macro_sector.name
#
#             if macro_sector not in sector_portfolio:
#                 res[macro_sector] = {
#                     "no_of_stocks": investment.quantity,
#                     "securities": [
#                         {
#                             "security": SecuritySerializerForSectorWisePortfolio(
#                                 security
#                             ).data,
#                             "quantity": investment.quantity,
#                         }
#                     ],
#                 }
#             else:
#                 sector_portfolio[macro_sector]["no_of_stocks"] += investment.quantity
#                 sector_portfolio[macro_sector]["securities"].append(
#                     {
#                         "security": SecuritySerializerForSectorWisePortfolio(
#                             security
#                         ).data,
#                         "quantity": investment.quantity,
#                     }
#                 )
#
#             total_stock_in_sector = sector_portfolio[macro_sector]["no_of_stocks"]
#             sector_portfolio[macro_sector]["allocation"] = round(
#                 (total_stock_in_sector / total_securities) * 100, 2
#             )
#
#         sector_wise_portfolio[portfolio_sector] = res
#
#     for k, v in sector_wise_portfolio.items():
#         for sector, data in v.items():
#             for sec in data["securities"]:
#                 sec["percentage"] = round(
#                     (sec["quantity"] / data["no_of_stocks"]) * 100, 2
#                 )
#
#     return sector_wise_portfolio


def get_securities_by_sector(investments):
    total_securities = sum(investment.quantity for investment in investments)

    sector_wise_portfolio = {
        "basic_industry": {},
        "industry": {},
        "sector": {},
        "macro_sector": {},
    }

    distinguish_by = {
        "basic_industry": lambda sec: sec.basic_industry.name,
        "industry": lambda sec: sec.basic_industry.industry.name,
        "sector": lambda sec: sec.basic_industry.industry.sector.name,
        "macro_sector": lambda sec: sec.basic_industry.industry.sector.macro_sector.name,
    }

    for portfolio_sector, res in sector_wise_portfolio.items():
        for investment in investments:
            security = investment.security
            sector_key = distinguish_by[portfolio_sector](security)

            if sector_key not in res:
                res[sector_key] = {
                    "no_of_stocks": 0,
                    "securities": [],
                }

            res[sector_key]["no_of_stocks"] += investment.quantity
            res[sector_key]["securities"].append(
                {
                    "security": SecuritySerializerForSectorWisePortfolio(security).data,
                    "quantity": investment.quantity,
                    "percentage": round(
                        (investment.quantity / res[sector_key]["no_of_stocks"]) * 100, 2
                    ),
                }
            )

        total_stock_in_sector = sum(data["no_of_stocks"] for data in res.values())
        for sector_data in res.values():
            sector_data["allocation"] = round(
                (sector_data["no_of_stocks"] / total_stock_in_sector) * 100, 2
            )

    return sector_wise_portfolio
