import datetime

from django.db import transaction

from data_import.models import TradeBook, InvestmentBook
from datahub.models import Security
from industries.views import get_basic_industry_object_from_industry_info
from scrapper.views import NSEScrapper


def append_security_symbol(headers=None):
    securities = Security.objects.filter(symbol__isnull=True)
    nse = NSEScrapper(headers)
    securities_to_update = []
    for security in securities:
        symbol = nse.get_symbol(security.name)
        print(symbol)
        if symbol:
            security.symbol = symbol
            securities_to_update.append(security)

    Security.objects.bulk_update(securities_to_update, fields=["symbol"])


def process_investment_books(headers=None):
    investment_books = InvestmentBook.objects.filter(processed=False)
    nse = NSEScrapper(headers)
    for investment_book in investment_books:
        symbol = nse.get_symbol(investment_book.security)
        if not symbol:
            continue
        security, created = Security.objects.get_or_create(symbol=symbol)
        update_security(headers, security.id, nse)
        investment_book.processed = True
        investment_book.save()
