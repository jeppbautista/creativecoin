from bs4 import BeautifulSoup
from forex_python.converter import CurrencyRates
import requests

import datetime


def get_usd():
    def _crawl_usd():
        URL = "https://www.exchangerates.org.uk/Dollars-to-Philippine-Pesos-currency-conversion-page.html"
        body = requests.get(URL)

        soup = BeautifulSoup(body.text)
        for conv in soup.find_all('div', class_='p_conv30'):
            try:
                return float(conv.find('span').find('span').text)
            except AttributeError:
                print("-- Crawl Failed using Forex-Python")
                pass

    try:
        return _crawl_usd()
    except Exception:
        c = CurrencyRates()
        return c.get_rates('USD')['PHP']


def sci_notation(x, decimal=10):
    return float(format(x, '.{}f'.format(decimal)))


def serialize_datetime(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")