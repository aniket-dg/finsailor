import difflib
from collections import defaultdict

import requests

from datahub.models import SecurityCache


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
    def __init__(self, headers=None):
        self.headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,nl;q=0.7",
            "cookie": "defaultLang=en; _ga=GA1.1.1029898552.1713530702; AKA_A2=A; "
            "_abck=4FE7987C27EF7A881A24B25F9EFAAE29~0"
            "~YAAQfwHVF0c3JgGPAQAAmywJCgtMM85emI5EqQl5rYwUaB9GeeqtTAwNoQQuAOu"
            "/BLwFQvaUp0qNR8uBv8BG8iJu5fOG3T35ZBCKr4UcGF3TtXMLhrYxSQnNBtS8OO6wF"
            "Nxq8EGBUDJOo7xuZWncE6R7BBwMlEGdQq5PHOxXbcJ9dFjPKFS9e3KNolTqER3W0TVZZ"
            "Z051JFLo1fR87HN4DeGFGwKA75jgJNDcb9HP5h7jBd79mt+HbsLLNExOeCaTKjGfiM9/0Q"
            "ND6zDXG4Dd45TxNial3+alURVzZgTOvFgS2NSug1gFSB2MCzFux3k4p/7nfUM6lsKjQ"
            "VbUvu6Y8435VbDdSaqH0EHwMj43EDzp9K1KTrcjBano3kWDCO6pSgtDM3w3au+fhi1Ga"
            "FuzjEyEPSWFZhl4oc=~-1~-1~-1; ak_bmsc=9DCBC935B6A9079F2C648A8981A6EA42"
            "~000000000000000000000000000000~YAAQfwHVF1g4JgGPAQAAjDUJCheXM4SzJZS92+"
            "IVkvTElnYZp/GnCHvweTrVvgPVwG+HfFdBirCZD4kEADHd5tdl3NLtlhv2xamQZdB3c1gLB"
            "adj6rK6QR6t9+D0BYEBsj69wMGKXVF/9FV9YRVQvorvtUF/pE2i3Le/d5nACyRgE0znsv0I66znPqm5eUeUnVGYhprr9sbgh"
            "+xJuw4HIAAw+V2ygnkzLF4lf7iPIkR3rCk/x9LWb7WQaimMnu6iYBzow6x0"
            "+AyrHwsDr8qwR4i8wVaA1lSgXk2WLzBlqMPtZ1PzxCB"
            "/OlKW3Mt5ppHb6tJhbGrZyfRBfTpEaNmTr2ulcYLdqjfsWO5A8PNy7huSHM7bY7l4fqr9v"
            "/6g3HS7FvG0GIrenerxQ67P0zIm5WvNpRHSVrHM/7tRMIGbQ9xkMPgWskvVS/2gbemeAVDknYj9YWh5cFloIVW4vZUX; "
            "nsit=AyEA1CEc0krZgc03C7twQQLe; _ga_QJZ4447QD3=GS1.1.1713860662.3.0.1713860662.0.0.0; "
            "nseappid=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
            ".eyJpc3MiOiJhcGkubnNlIiwiYXVkIjoiYXBpLm5zZSIsImlhdCI6MTcxMzg2MDcyNCwiZXhwIjoxNzEzODY3OTI0fQ"
            ".lalSDys19a5S4eLI9qgpEsMAFIr_d4qpu_xvofA4X4E; "
            "bm_sz=70CED1EB7F9737A98C55DC466212A5F1~YAAQbQHVF1KLRAGPAQAAnEcPCheZQtW4DsYXNETZaMykfRC"
            "+YJG8P6YO63iVau/I1Na"
            "/p7WxnHb3elhLEIa96nSziHisywdqbHmLd7eJdoLTKqDhGs0m1iYwJnQusx0RSMjUpnGRDxhlJwG"
            "/8St6JcIikYTZ3vJEn9MZLHYN/CBLkXHnDSfEYFniXYW+pMVabTw/uGHbRAjkl0"
            "/E8Crn7jEY9k7fxz4NeA8eybgkuBh5umG4jMG3Qjd3jdgBzfrEzc4k01fI2MDq5dY6EU4TiS3THXZp0"
            "/SWAkoeO2LnWYWeXw7KfWYanyWjPdY2XwF3dA/W8NUG2nmo1BfxeJFplOd1nGuUv0u96n+u/r4IiWdh4idru"
            "+1KkGPjV93XFi/uL0D+Db4asgV99j+P6O+9VZKXtd+g8lMYMhkSn93ZOvOl085Adicig/lra8a3UbsChUERwE18"
            "~4337985~3490352; _ga_87M7PJ3R97=GS1.1.1713860326.4.1.1713860725.0.0.0; nseQuoteSymbols=[{"
            '"symbol":"PBAINFRA","identifier":null,"type":"equity"},{"symbol":"PNB","identifier":null,'
            '"type":"equity"}]; RT="z=1&dm=nseindia.com&si=2564c1a3-7984-4260-89e3-945754e03b23&ss=lvc46oxw'
            '&sl=7&se=8c&tt=7kx&bcn=%2F%2F684d0d44.akstat.io%2F&ld=8mx8"; '
            "bm_sv=A8B522B8700CC95E343DC9F2D3117286~YAAQjgHVFz7ELAGPAQAAd"
            "/0PChdq560KyQKhSqpzIYgihH6ofyqyLgxGBfNWzlzY/5JjvTrVY4yLza7Y+pt/Jfcp9kVm0Kzct9tS"
            "/XzXbMSs7mZWuD3B9RkTKaOcJSOR0OnDytdR8bAsGqvd0It/dVhv4yE"
            "/bSGZdYXPk5LVoCNEI8NBCvsecyKHVtEUTPTdCOOKAqPdaKEis+IRwDgZ4objS7bY7JfAZwy6zl0iOr"
            "/Ogw5tJootvMKt9Rhewv8XWvON~1",
            "referer": "https://www.nseindia.com/get-quotes/equity?symbol=PNB",
            "sec-ch-ua": 'Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "macOS",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        self.cache = NSECache
        if headers:
            self.headers = headers

    def load_url(self, url):
        response = requests.get(url=url, headers=self.headers)
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
