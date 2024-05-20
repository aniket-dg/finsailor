from datetime import datetime
from typing import List

import pandas as pd
from django.shortcuts import render

from data_import.models import MutualFundBook
from datahub.tasks import update_security_price
from datahub.models import Security
from scrapper.views import NSEScrapper


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
