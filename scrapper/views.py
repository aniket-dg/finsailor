import datetime
import difflib
from collections import defaultdict
from typing import Dict

import requests
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from combo_investment import settings
from combo_investment.exception import APIBadRequest
from datahub.models import SecurityCache, Security
from scrapper.serializers import SecuritySymbolSerializer


def find_max_matching_string(target, string_list):
    max_score = 0
    max_matching_string = None

    for string in string_list:
        # Calculate the match score between the target string and the current string
        score = difflib.SequenceMatcher(None, target, string).ratio()

        # Update max_score and max_matching_string if the current score is higher
        if score > max_score:
            max_score = score
            max_matching_string = string

    return max_matching_string


class NSECache:
    def __init__(self):
        pass

    @classmethod
    def get_symbol(cls, scrip_name):
        security_cache = SecurityCache.objects.filter(name=scrip_name).last()
        if security_cache:
            return security_cache.symbol

        return None

    @classmethod
    def get_db_symbol(cls, scrip_name):
        security_id_names = Security.objects.filter(
            security_info__tradingStatus="Active"
        ).values("id", "name", "symbol")

        best_match = max(
            (entry for entry in security_id_names if entry["name"] is not None),
            key=lambda entry: difflib.SequenceMatcher(
                None, scrip_name, entry["name"]
            ).ratio(),
        )
        if best_match:
            return best_match["symbol"]

        return None

    @classmethod
    def set_symbol(cls, scrip_name, symbol):
        security_cache = SecurityCache(name=scrip_name, symbol=symbol)
        security_cache.save()
        return


class NSEScrapper:
    def __init__(self, session_refresh_interval=300):
        self._session_init_time = None
        self.cache = NSECache
        self.session_refresh_interval = session_refresh_interval
        self._session = requests.session()
        self.base_url = settings.NSE_BASE_URL
        self.create_session()

    @classmethod
    def nse_headers(cls):
        """
        Builds right set of headers for requesting http://nseindia.com
        :return: a dict with http headers
        """
        return {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/112.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }

    def create_session(self):
        print("Creating new NSE session.....")
        self._session = requests.Session()
        self._session.headers.update(self.nse_headers())
        self._session.get(self.base_url)
        self._session_init_time = datetime.datetime.now()
        print("Session created...")

    def load_url(self, url, params=None):
        time_diff = datetime.datetime.now() - self._session_init_time
        if time_diff.seconds > self.session_refresh_interval:
            self.create_session()

        response = self._session.get(
            url,
            params=params,
        )

        print(response.url)

        if response.status_code == 200:
            return response.json(), response.status_code

        raise APIBadRequest(
            {"text": response.text, "status_code": response.status_code}
        )

    def get_symbol(self, scrip_name):
        print("scrip_name")
        symbol = self.cache.get_symbol(scrip_name=scrip_name)
        if symbol:
            return symbol

        url = settings.NSE_SEARCH_SYMBOL_API_URL + scrip_name
        print(f"Fetching symbol for security - {scrip_name}")
        response, status_code = self.load_url(url)
        if status_code != 200:
            return "Unable to search given symbol"

        symbols = response.get("symbols")

        symbol_name_to_symbol_data = defaultdict(list)
        for symbol in symbols:
            if (
                symbol["result_type"] == "symbol"
                and symbol["result_sub_type"] == "equity"
            ):
                symbol_name_to_symbol_data[symbol["symbol_info"].lower()].append(symbol)

        max_match_symbol_info = find_max_matching_string(
            scrip_name.lower(), symbol_name_to_symbol_data.keys()
        )

        symbol = symbol_name_to_symbol_data.get(max_match_symbol_info)
        print(symbol)
        if symbol:
            if len(symbol) > 1:
                all_matching_symbols = [sym["symbol"] for sym in symbol]
                max_matching_symbol = find_max_matching_string(
                    scrip_name, all_matching_symbols
                )
                symbol = max_matching_symbol
            else:
                symbol = symbol[0]["symbol"]

            self.cache.set_symbol(scrip_name=scrip_name, symbol=symbol)
        else:
            symbol = self.cache.get_db_symbol(scrip_name=scrip_name)
            if symbol is None:
                raise Exception("Symbol not found for scrip -  ", scrip_name)

            self.cache.set_symbol(scrip_name=scrip_name, symbol=symbol)

        return symbol if symbol else None

    def get_quote_by_symbol(self, symbol):
        url = settings.NSE_SYMBOL_QUOTE_API_URL
        params = {
            "symbol": symbol,
        }
        print(f"Fetching Quote for security - {symbol}")

        response, status_code = self.load_url(url, params=params)
        if status_code != 200:
            return f"Unable to get given quote - {url} - {response}", status_code

        quote = response

        return quote, status_code

    def get_trade_info_by_symbol(self, symbol):
        url = settings.NSE_SYMBOL_QUOTE_API_URL
        params = {"symbol": symbol, "section": "trade_info"}
        print(f"Fetching Trade Info for security - {symbol}")

        response, status_code = self.load_url(url, params=params)
        if status_code != 200:
            return f"Unable to get given quote - {url} - {response}", status_code

        quote = response

        return quote, status_code

    def get_historical_data_by_symbol(self, symbol, from_date, to_date):
        url = settings.NSE_HISTORICAL_DATA_API_URL

        params = {
            "symbol": symbol,
            "from": from_date.date().strftime("%d-%m-%Y"),
            "to": to_date.date().strftime("%d-%m-%Y"),
        }
        data, status_code = self.load_url(url, params=params)

        return data, status_code

    def get_stocks_indices(self):
        url = settings.NSE_STOCK_INDICES_API_URl

        data, status_code = self.load_url(url)

        return data, status_code

    def get_historical_stock_indices_data(self, index, from_date, to_date):
        url = settings.NSE_STOCK_INDICES_HISTORICAL_DATA_API_URL
        params = {
            "indexType": index,
            "from": from_date.date().strftime("%d-%m-%Y"),
            "to": to_date.date().strftime("%d-%m-%Y"),
        }

        data, status_code = self.load_url(url, params=params)
        return data.get("data"), status_code

    def get_index_stocks(self, index_symbol):
        url = settings.NSE_STOCK_INDEX_DETAIL_API_URL + index_symbol

        data, status_code = self.load_url(url)

        return data, status_code

    def get_upcoming_events(self):
        url = settings.NSE_UPCOMING_EVENTS_API_URL

        data, status_code = self.load_url(url)

        return data, status_code

    def get_corporate_actions(self, symbol, from_date=None, to_date=None):
        url = settings.NSE_CORPORATE_ACTIONS_API_URL
        if from_date is None:
            from_date = (
                (datetime.datetime.now() - datetime.timedelta(days=7300))
                .date()
                .strftime("%d-%m-%Y")
            )
        if to_date is None:
            to_date = (
                (datetime.datetime.now() + datetime.timedelta(days=365))
                .date()
                .strftime("%d-%m-%Y")
            )
        params = {
            "index": "equities",
            "from_date": from_date,
            "to_date": to_date,
            "symbol": symbol,
        }

        data, status_code = self.load_url(url, params=params)

        return data, status_code

    def get_holidays(self) -> Dict:
        url = settings.NSE_HOLIDAYS_LIST_API_URL

        data, status_code = self.load_url(url)

        return data


@extend_schema(tags=["NSE Scrapper"])
class NSEViewSet(APIView):
    @extend_schema(parameters=[SecuritySymbolSerializer])
    def get(self, *args, **kwargs):
        nse = NSEScrapper()
        symbol = self.request.query_params.get("symbol")
        quote = nse.get_quote_by_symbol(symbol)
        return Response(quote)
