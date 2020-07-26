import base64
from bs4 import BeautifulSoup
from forex_python.converter import CurrencyRates
import requests

import datetime
import hashlib

def generate_txn_id(salt):
    return hashlib.sha512("{}-{}".format(serialize_datetime(utcnow()), salt)\
            .encode("utf-8")).hexdigest()

def generate_referral_id(salt=1):
    salt_padded = str(salt).zfill(4)
    salt_bytes = salt_padded.encode("utf-8")
    b64_salt = base64.b64encode(salt_bytes)
    return b64_salt.decode('utf-8')

def encode_referral_id(enc):
    enc_bytes = enc.encode('utf-8')
    decode_bytes = base64.b64decode(enc_bytes)
    raw_ref = decode_bytes.decode('utf-8')
    return int(raw_ref.replace('ccn', ''))


def get_usd():
    def _crawl_usd():
        URL = "https://www.exchangerates.org.uk/Dollars-to-Philippine-Pesos-currency-conversion-page.html"
        body = requests.get(URL)

        soup = BeautifulSoup(body.text)
        for conv in soup.find_all('div', class_='p_conv30'):
            try:
                return float(conv.find('span').find('span').text)
            except AttributeError as e:
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


def utcnow():
    return datetime.datetime.utcnow()