import logging
from _decimal import Decimal
from datetime import datetime
from typing import List
import django_filters
from django_filters import FilterSet

import pandas as pd
from django.db.models import Q
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from data_import.models import MutualFundBook
from datahub.tasks import update_security_price
from datahub.models import Security
from mutual_funds.models import Fund, FundInvestment
from mutual_funds.serializers import FundInvestmentSerializer
from scrapper.views import NSEScrapper

logger = logging.getLogger("MutualFunds")


# Create your views here.
class MutualFund:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run

    def import_data_from_report(self, file_path) -> List[MutualFundBook]:
        print(self.dry_run)
        df_initial = pd.read_excel(file_path, sheet_name="Transactions", header=None)
        header_row_index = df_initial[
            df_initial.apply(
                lambda row: row.astype(str).str.contains("Scheme Name").any(), axis=1
            )
        ].index[0]
        df = pd.read_excel(
            file_path, sheet_name="Transactions", header=header_row_index
        )
        df_cleaned = df.dropna(axis=1)
        df_cleaned = df.dropna(how="all")
        mf_to_create = []
        for i, row in df_cleaned.iterrows():
            date_string = row["Date"]
            date = datetime.strptime(date_string, "%d %b %Y").date()
            amount = row["Amount"].replace(",", "")
            mf_book = MutualFundBook(
                scheme_name=row["Scheme Name"],
                units=row["Units"],
                transaction_type=row["Transaction Type"],
                nav=row["NAV"],
                amount=amount,
                date=date,
            )
            mf_to_create.append(mf_book)

        created_mf_book = MutualFundBook.objects.bulk_create(mf_to_create)
        return created_mf_book

    def get_or_create_security(self, name):
        nse = NSEScrapper()
        symbol = nse.get_symbol(name)
        security, created = Security.objects.get_or_create(
            symbol=symbol, defaults={"name": name}
        )
        if created:
            update_security_price.delay(security.id)
        return security

    def get_or_create_fund(self, name):
        fund, created = Fund.objects.get_or_create(scheme_name=name)
        return fund


class MutualFundInvestment:
    def __init__(self, user=None):
        self.mf_books_to_process = (
            MutualFundBook.objects.filter(user=user)
            .filter(investment_processed=False)
            .order_by("date")
        )
        self.user = user
        self.mutual_fund = MutualFund()

    def process_mf_books(self):
        fund_investments = []
        for mf_book in self.mf_books_to_process:
            fund = self.mutual_fund.get_or_create_fund(mf_book.scheme_name)
            if not fund:
                logger.warning(f"Fund {fund} not found")
                continue

            fund_investment = FundInvestment.objects.filter(
                user=self.user, fund_id=fund.id
            ).last()
            if fund_investment is None:
                fund_investment = FundInvestment(
                    user=self.user,
                    fund_id=fund.id,
                )
            nav = Decimal(mf_book.nav)
            units = Decimal(mf_book.units)
            fund_investment.nav_purchased.append(nav)
            fund_investment.units_purchased.append(units)
            fund_investment.units += Decimal(units)

            amount_invested = 0
            all_nav = fund_investment.nav_purchased
            all_units = fund_investment.units_purchased

            for nav, unit in zip(all_nav, all_units):
                amount = nav * unit
                amount_invested += amount

            print(fund, amount_invested, "amount_invested")

            fund_investment.avg_nav = amount_invested / len(all_units)
            fund_investment.save()
            fund_investments.append(fund_investment)

            mf_book.investment_processed = True
            mf_book.save()

        return fund_investments


class FundInvestmentFilter(FilterSet):
    # symbol = django_filters.CharFilter(method="filter_by_security_symbol")

    # name = django_filters.CharFilter(field_name="name", lookup_expr="contains")
    # id = django_filters.CharFilter(method="filter_by_ids")
    #
    # def filter_by_security_symbol(self, queryset, name, value):
    #     symbols = value.split(",")
    #     return queryset.filter(security__symbol__in=symbols)

    class Meta:
        model = FundInvestment
        fields = ("fund",)


@extend_schema(tags=["Mutual Fund Investment App"], methods=["GET", ""])
class FundInvestmentViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        return FundInvestmentSerializer

    def get_queryset(self):
        qs = FundInvestment.objects.filter(units__gt=0)

        filter_qs = self.filter_queryset(qs)

        return filter_qs
