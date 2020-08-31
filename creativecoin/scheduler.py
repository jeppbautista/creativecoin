from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
from forex_python.converter import CurrencyRates
import requests

import os
import re
import traceback

from creativecoin import app
from creativecoin.email import EmailSender
from creativecoin.helper.utils import get_usd

# def _run_grain_crawler():
    
#     try:
#         url = "https://goldprice.com/gold-price-per-gram/"

#         page = requests.get(url)

#         soup = BeautifulSoup(page.content, features='html.parser')
#         soup = soup.find('table', class_='nfusion-table-border')\
#                     .find('tbody')\
#                     .find('td', class_='quote-field ask')\
#                     .find('span')

#         raw_value = soup.text
#         value = re.sub(r"\$\s+", "", raw_value)


#         grain_value = round((float(value)/15.4324),2)

#         file_content = '{"grain_value": '+str(grain_value)+'}'
#         print(file_content)

#         with open('creativecoin/static/data/grain.json', 'w') as f:
#             f.write(file_content)
            
#         app.logger.info("Grain value set to: {}".format(grain_value))
#     except Exception as e:
#         # TODO send notification about error
#         app.logger.error("Failed setting grain_value")
    

def run_scheduled_jobs():
    def foobar():
        app.logger.error("ERROR - FOO FOO FOO")

    from flask_apscheduler import APScheduler
    try:
        scheduler = APScheduler()
        scheduler.init_app(app)
        scheduler.add_job(func=foobar, trigger='interval', seconds=20, id="foobar")
        scheduler.start()
    except Exception:
        app.logger.error(traceback.format_exc())



    

# if __name__ == "__main__":
#     get_usd()