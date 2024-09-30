import datetime
import math
from collections import defaultdict
from zoneinfo import ZoneInfo
import logging

from celery import shared_task, chain
from django.db import IntegrityError

from combo_investment import settings
from combo_investment.celery import BaseTaskWithRetry
from data_import.models import TradeBook
from datahub.models import Security, StockIndex, TodayStockIndex, Holiday
from datahub.utils import get_all_securities, process_corporate_actions
from industries.views import get_basic_industry_object_from_industry_info
from scrapper.views import NSEScrapper
from user_investment.models import Investment
from user_investment.views import UserInvestment
from industries.tasks import calculate_todays_performance

logger = logging.getLogger("Datahub")


def process_trade_books():
    trade_books = TradeBook.objects.filter(processed=False)
    nse = NSEScrapper()
    for trade_book in trade_books:
        symbol = nse.get_symbol(trade_book.security)
        if not symbol:
            continue
        security = Security.objects.filter(symbol=symbol).last()
        if security is None:
            security = Security(symbol=symbol)
        updated_security = update_security_price(security, nse)
        updated_security.save()
        trade_book.processed = True
        trade_book.save()


@shared_task(base=BaseTaskWithRetry)
def update_security_price(security_id):
    security = Security.objects.get(id=security_id)
    nse = NSEScrapper()

    quote, status_code = nse.get_quote_by_symbol(security.symbol)
    if status_code != 200:
        print("Error", quote)

    if "error" in quote:
        logger.warning(
            f"Error occurred while updating security{security.id} - {security.symbol}, Error : {quote.get('message')}"
        )
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
    metadata = quote.get("metadata")
    # if not security.isin:
    security.isin = metadata.get("isin")
    if not security.name:
        security.name = info.get("companyName")

    # Security Info
    security_info = quote.get("securityInfo")
    if not security.security_info:
        security.security_info = security_info

    # Metadata Info
    metadata = quote.get("metadata")
    security.metadata = metadata

    security.last_updated_price = (
        price_info.get("close")
        if price_info.get("close")
        else price_info.get("lastPrice")
    )
    local_tz = ZoneInfo(settings.TIME_ZONE)
    security.price_modified_datetime = datetime.datetime.now().astimezone(local_tz)
    security.save()
    logger.info(f"{security.symbol} Security updated!")
    return security


@shared_task(base=BaseTaskWithRetry)
def update_all_securities_prices():
    securities_id_to_exclude = []
    investments = Investment.objects.all()
    for investment in investments:
        update_security_price.delay(investment.security_id)
        securities_id_to_exclude.append(investment.security_id)
    securities = Security.objects.filter(base_security=True).exclude(
        id__in=securities_id_to_exclude
    )

    for sec in securities:
        update_security_price.delay(sec.id)
    logger.info("All securities prices updated")


@shared_task(base=BaseTaskWithRetry)
def update_historical_prices(security_id, from_year, to_date):
    user_investment = UserInvestment()
    user_investment.update_security_for_historical_prices(
        security_id, from_year=from_year, to_date=to_date
    )
    logger.info(f"Security {security_id} is updated for historical prices.")


@shared_task(base=BaseTaskWithRetry)
def update_trade_info_of_securities():
    securities = Security.objects.filter(base_security=True)
    nse = NSEScrapper()
    for security in securities:
        data, status = nse.get_trade_info_by_symbol(security.symbol)
        market_dept_order_book = data.get("marketDeptOrderBook")
        security_wise_dp = data.get("securityWiseDP")

        if market_dept_order_book is None or security_wise_dp is None:
            print(f"Trade Info not found for security {security.id}-{security.symbol}")
            continue

        date_str = security_wise_dp.get("secWiseDelPosDate")

        try:
            date_object = datetime.datetime.strptime(date_str, "%d-%b-%Y %H:%M:%S")
        except ValueError as e:
            date_object = datetime.datetime.now().astimezone(
                ZoneInfo(settings.TIME_ZONE)
            )
        trade_info = market_dept_order_book.get("tradeInfo")
        security.market_cap = trade_info.get("totalMarketCap")
        security.free_float_market_cap = trade_info.get("ffmc")
        security.trade_info = {date_object.date().isoformat(): data}
        security.save()


@shared_task(
    base=BaseTaskWithRetry,
    options={"queue": "scheduled", "retry": True},
)
def run_every_30_sec():
    logger.info("Printing every 30 second........")


@shared_task(base=BaseTaskWithRetry)
def update_stock_indices_from_nse():
    nse = NSEScrapper()
    stock_indices, status = nse.get_stocks_indices()

    historical_dates_info = stock_indices.get("dates")
    date_30_day_ago = stock_indices.get("date30dAgo")
    date_365_day_ago = stock_indices.get("date365dAgo")
    stock_indices_data = stock_indices.get("data")
    today_stock_index_indices = []

    stock_index_date = datetime.datetime.strptime(
        stock_indices.get("timestamp"), "%d-%b-%Y %H:%M"
    )

    today_stock_index = TodayStockIndex.objects.filter(
        date=stock_index_date.date()
    ).last()
    if today_stock_index is None:
        today_stock_index = TodayStockIndex(date=stock_index_date.date())
        today_stock_index.historical_dates_info = historical_dates_info
        today_stock_index.date_30_day_ago = datetime.datetime.strptime(
            date_30_day_ago, "%d-%b-%Y"
        )
        today_stock_index.date_365_day_ago = datetime.datetime.strptime(
            date_365_day_ago, "%d-%b-%Y"
        )
        today_stock_index.save()

    for stock_index in stock_indices_data:
        stock_index["date"] = stock_index_date.date()
        stock_index["time"] = stock_index_date.time()
        stock_index_obj, created = StockIndex.update_or_create_from_dict(stock_index)

        today_stock_index_indices.append(stock_index_obj.id)

    today_stock_index.stocks_indices.all().delete()
    today_stock_index.stocks_indices.add(*today_stock_index_indices)


def update_historical_data_of_stock_indices(from_date, to_date):
    stock_indexes = StockIndex.objects.distinct("index")
    nse = NSEScrapper()
    local_tz = ZoneInfo(settings.TIME_ZONE)
    for stock_index in stock_indexes:
        data, status_code = nse.get_historical_stock_indices_data(
            stock_index.index, from_date, to_date
        )
        for index_data in data.get("indexCloseOnlineRecords"):
            new_index = stock_index.get_empty_object()
            datetime_object = datetime.datetime.fromisoformat(
                index_data.get("TIMESTAMP").replace("Z", "+00:00")
            )
            dt_local = datetime_object.astimezone(local_tz)
            new_index.open = index_data.get("EOD_OPEN_INDEX_VAL")
            new_index.high = index_data.get("EOD_HIGH_INDEX_VAL")
            new_index.low = index_data.get("EOD_LOW_INDEX_VAL")
            new_index.last = index_data.get("EOD_CLOSE_INDEX_VAL")
            new_index.date = dt_local.date()
            new_index.time = dt_local.time()
            try:
                new_index.save()
            except IntegrityError as e:
                pass


@shared_task(base=BaseTaskWithRetry)
def update_index_stocks(index_id):
    stock_index = StockIndex.objects.get(id=index_id)
    nse = NSEScrapper()
    index_stocks, status = nse.get_index_stocks(index_symbol=stock_index.indexSymbol)

    stocks = index_stocks.get("data")

    if stocks is None:
        return

    for stock in stocks:
        security = Security.objects.filter(symbol=stock.get("symbol")).last()
        if security is None:
            security = Security(symbol=stock.get("symbol"))

        last_price = stock.get("lastPrice")
        last_update_time = stock.get("lastUpdateTime")

        last_updated_time = datetime.datetime.strptime(
            last_update_time, "%d-%b-%Y %H:%M:%S"
        )
        security.last_updated_price = last_price
        security.price_modified_datetime = last_updated_time
        historical_price_info = security.historical_price_info or {}
        historical_price_info[last_updated_time.date().isoformat()] = stock
        security.historical_price_info = historical_price_info
        security.save()


@shared_task(base=BaseTaskWithRetry)
def process_nse_holidays():
    nse = NSEScrapper()
    holidays = nse.get_holidays()

    for key, holidays in holidays.items():
        for holiday_data in holidays:
            trading_date = datetime.datetime.strptime(
                holiday_data.get("tradingDate"), "%d-%b-%Y"
            ).date()
            holiday = Holiday.objects.get_or_create(
                trading_date=trading_date,
                weekday=holiday_data.get("weekDay"),
                description=holiday_data.get("description"),
                sr_no=holiday_data.get("Sr_no"),
            )


def securities_stats():
    res = defaultdict(list)
    securities = get_all_securities()
    for security in securities:
        last_historical_price_data_key = sorted(security.historical_price_info.keys())[
            -1
        ]
        last_historical_price_data = security.historical_price_info[
            last_historical_price_data_key
        ]
        last_price = last_historical_price_data.get("lastPrice")
        last_close = last_historical_price_data.get("previousClose")
        if last_price is None or last_close is None:
            print("Skip", security.id)
            continue
        if last_close != 0:
            percent_change = ((last_price - last_close) / last_close) * 100
            res[math.floor(percent_change)].append(
                {
                    "security_id": security.id,
                    "p_change": float(percent_change),
                    "change": last_price - last_close,
                }
            )

    return res


@shared_task
def calculate_security_prices_sector_performance():
    # signature = chain(update_all_securities_prices.s(), calculate_todays_performance.s())
    # signature()
    #
    # callback_signature = update_all_securities_prices.signature(
    #     immutable=True,
    #     link=calculate_todays_performance.signature(immutable=True),
    #     link_error=calculate_todays_performance.signature(immutable=True),
    # )
    # #
    # callback_signature()

    callback = calculate_todays_performance.signature(immutable=True)

    update_all_securities_prices.apply_async(
        link=callback,
        link_error=callback,
    )


@shared_task(base=BaseTaskWithRetry)
def process_corporate_actions_task():
    securities = get_all_securities()
    nse = NSEScrapper()
    for security in securities:
        process_corporate_actions(nse=nse, security=security)
