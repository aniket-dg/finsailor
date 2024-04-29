import datetime
import difflib
import time
from collections import defaultdict

import requests

from datahub.models import SecurityCache
from fake_useragent import UserAgent


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
        self.base_url = "https://www.nseindia.com"
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

        return response.text, response.status_code

    def get_symbol(self, scrip_name):
        symbol = self.cache.get_symbol(scrip_name=scrip_name)
        if symbol:
            return symbol

        url = f"https://www.nseindia.com/api/search/autocomplete?q={scrip_name}"
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

        if len(symbol) > 1:
            all_matching_symbols = [sym["symbol"] for sym in symbol]
            max_matching_symbol = find_max_matching_string(
                scrip_name, all_matching_symbols
            )
            symbol = max_matching_symbol
        else:
            symbol = symbol[0]["symbol"]

        if symbol:
            self.cache.set_symbol(scrip_name=scrip_name, symbol=symbol)

        return symbol if symbol else None

    def get_quote_by_symbol(self, symbol):
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
        print(f"Fetching Quote for security - {symbol}")

        response, status_code = self.load_url(url)
        if status_code != 200:
            return f"Unable to get given quote - {url} - {response}", status_code

        quote = response

        return quote, status_code

    def get_historical_data_by_symbol(self, symbol, from_date, to_date):
        url = "https://www.nseindia.com/api/historical/cm/equity"

        params = {
            "symbol": symbol,
            "from": from_date.date().strftime("%d-%m-%Y"),
            "to": to_date.date().strftime("%d-%m-%Y"),
        }
        data, status_code = self.load_url(url, params=params)

        return data, status_code
