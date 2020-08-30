from bs4 import BeautifulSoup
import requests
import traceback

from creativecoin import app
from creativecoin.email import EmailSender

def get_grain_value():
    mail = EmailSender()
    TROY_OUNCE = 0.002083333

    try:
        url = "http://www.goldgrambars.com/calculator/"
        body = requests.get(url)
        soup = BeautifulSoup(body.text)
        raw_price = soup.select_one("input[name='goldprice']").get("value")
        price = float(raw_price)
        
    except Exception:
        message = traceback.format_exc()
        mail.send_mail(app.config["ADMIN_MAIL"], "Grain value crawling failed!", message)

        headers = {
            'x-access-token': 'goldapi-1c3xvykegrbtei-io',
        }

        try:
            response = requests.get("https://www.goldapi.io/api/XAU/USD")
            if response.status_code != 200:
                mail.send_mail(app.config["ADMIN_MAIL"], "Grain value API failed!", message)
                return -1

            raw_price = response.json()["price"]
            price = float(raw_price)
        except Exception:
            mail.send_mail(app.config["ADMIN_MAIL"], "Grain value API failed!", message)
            return -1

    return (price*TROY_OUNCE)*0.05


    