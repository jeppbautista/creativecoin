import base64
from bs4 import BeautifulSoup
import datetime
import hashlib
from forex_python.converter import CurrencyRates
import requests
import traceback

import os

from creativecoin import app
from creativecoin.email import EmailSender


def generate_txn_id(salt):
    return hashlib.sha1("{}-{}".format(serialize_datetime(utcnow()), str(salt))\
            .encode("utf-8")).hexdigest()


def generate_wallet_id(salt):
    return hashlib.md5(str(salt).encode("utf-8")).hexdigest()


def generate_referral_id(salt=1):
    salt_padded = str(salt).zfill(5)
    salt_bytes = salt_padded.encode("utf-8")
    b64_salt = base64.b64encode(salt_bytes)
    return b64_salt.decode('utf-8')


def encode_referral_id(enc):
    enc_bytes = enc.encode('utf-8')
    decode_bytes = base64.b64decode(enc_bytes)
    raw_ref = decode_bytes.decode('utf-8')
    return int(raw_ref.replace('ccn', ''))


def crawl_usd():
    def _crawl_usd():
        URL = "https://www.exchangerates.org.uk/Dollars-to-Philippine-Pesos-currency-conversion-page.html"
        body = requests.get(URL)

        soup = BeautifulSoup(body.text, "html.parser")
        for conv in soup.find_all('div', {"id":"shd2a"}):
            try:
                file_usd = app.config["FILE_USD"]

                with open(os.path.join(os.getcwd(), file_usd), "w+") as f:
                    f.write(str(float(conv.find('span').text)))

                return float(conv.find('span').text)
            except AttributeError as e:
                app.logger.error(traceback.format_exc())
                app.logger.error("ERROR - Crawl Failed. Using Forex-Python")

    mail = EmailSender()

    try:
        if not _crawl_usd():
            raise Exception("unable to crawl")
    except Exception:
        app.logger.error(traceback.format_exc())
        c = CurrencyRates()
        try:
            file_usd = app.config["FILE_USD"]

            with open(os.path.join(os.getcwd(), file_usd), "w+") as f:
                f.write(str(float(c.get_rates('USD')['PHP'])))

            return float(c.get_rates('USD')['PHP'])
        except Exception:
            app.logger.error(traceback.format_exc())
            message = traceback.format_exc()
            with open(os.path.join(os.getcwd(), file_usd), "w+") as f:
                mail.send_mail(app.config["ADMIN_MAIL"], "USD value crawling failed!", message)
                f.write(str(50.0))
  
    return 50.0


def crawl_grain():
    mail = EmailSender()
    TROY_OUNCE = 0.002083333
    OUNCE_TO_GRAM = 31.1035
    GRAM_TO_GRAIN = 15.4324

    file_grain = app.config["FILE_GRAIN"]
    file_grain = os.path.join(os.getcwd(), file_grain)

    try:
        url = "http://www.goldgrambars.com/calculator/"
        body = requests.get(url)
        soup = BeautifulSoup(body.text)
        raw_price = soup.select_one("input[name='goldprice']").get("value")
        price = float(raw_price)
        
    except Exception:
        app.logger.error(traceback.format_exc())
        message = traceback.format_exc()
        mail.send_mail(app.config["ADMIN_MAIL"], "Grain value crawling failed!", message)

        headers = {
            'x-access-token': 'goldapi-1c3xvykegrbtei-io',
        }

        try:
            response = requests.get("https://www.goldapi.io/api/XAU/USD")
            if response.status_code != 200:
                mail.send_mail(app.config["ADMIN_MAIL"], "Grain value API failed!", message)
                with open(file_grain, "w+") as f:
                    f.write(str(3.5))
                return 3.5

            raw_price = response.json()["price"]
            price = float(raw_price)
        except Exception:
            app.logger.error(traceback.format_exc())
            message = traceback.format_exc()
            mail.send_mail(app.config["ADMIN_MAIL"], "Grain value API failed!", message)
            with open(file_grain, "w+") as f:
                f.write(str(3.5))
            return 3.5

    with open(file_grain, "w+") as f:
        f.write(str((price/OUNCE_TO_GRAM)/GRAM_TO_GRAIN))

    return (price/OUNCE_TO_GRAM)/GRAM_TO_GRAIN


def diff_month(d1, d2):
    return int((d1.year - d2.year) * 12 + d1.month - d2.month)


def get_usd():
    app.logger.error("INFO - Getting USD...")
    file_usd = app.config["FILE_USD"]

    with open(os.path.join(os.getcwd(), file_usd), "r") as f:
        usd = f.read()
    app.logger.error("INFO - Extracted USD: {}".format(usd))

    return float(usd)


def get_grain():
    app.logger.error("INFO - Getting grain value...")
    file_grain = app.config["FILE_GRAIN"]

    with open(os.path.join(os.getcwd(), file_grain), "r") as f:
        grain = f.read()

    # m = diff_month(datetime.datetime.now(), datetime.datetime.strptime("2021-02-01", "%Y-%m-%d"))
    # grain = float(grain) + float(grain) * (0.05 * m)

    app.logger.error("INFO - Extracted grain value: {}".format(grain))

    return float(grain)


def sci_notation(x, decimal=10):
    return float(format(x, '.{}f'.format(decimal)))


def serialize_datetime(dt):
    if type(dt) == str:
        return datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def truncate_string(string, strlen=20):
    return string[:strlen]+"..."+string[-1]


def utcnow():
    return datetime.datetime.utcnow()
