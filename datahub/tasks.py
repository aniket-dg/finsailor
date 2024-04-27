import datetime

from data_import.models import TradeBook
from datahub.models import Security
from industries.views import get_basic_industry_object_from_industry_info
from scrapper.views import NSEScrapper


def process_trade_books(headers=None):
    trade_books = TradeBook.objects.filter(processed=False)
    nse = NSEScrapper(headers)
    for trade_book in trade_books:
        symbol = nse.get_symbol(trade_book.security)
        if not symbol:
            continue
        security = Security.objects.filter(symbol=symbol).last()
        if security is None:
            security = Security(symbol=symbol)
        updated_security = update_security(headers, security, nse)
        updated_security.save()
        trade_book.processed = True
        trade_book.save()


def update_security(headers, security, nse):
    if not nse:
        nse = NSEScrapper(headers)

    quote, status_code = nse.get_quote_by_symbol(security.symbol)
    if status_code != 200:
        print("Error", quote)
        return

    # Industry data
    industry_info = quote.get("industryInfo")
    basic_industry = get_basic_industry_object_from_industry_info(industry_info)
    if not security.basic_industry:
        security.basic_industry = basic_industry

    # Price data
    price_info = quote.get("priceInfo")
    today_date = datetime.datetime.now().date().isoformat()
    historical_price_info = security.historical_price_info
    historical_price_info[today_date] = price_info
    security.historical_price_info = historical_price_info

    # Info
    info = quote.get("info")
    if not security.isin:
        security.isin = info.get("isin")
    if not security.name:
        security.name = info.get("companyName")

    # Security Info
    security_info = quote.get("securityInfo")
    if not security.security_info:
        security.security_info = security_info

    # Metadata Info
    metadata = quote.get("metadata")
    security.metadata = metadata

    security.last_updated_price = price_info.get("lastPrice")
    security.price_modified_datetime = datetime.datetime.now()
    return security
