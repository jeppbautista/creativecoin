import os
import re

from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
import requests

from creativecoin import app

@app.before_first_request
def _run_grain_crawler():
    
    try:
        url = "https://goldprice.com/gold-price-per-gram/"

        page = requests.get(url)

        soup = BeautifulSoup(page.content, features='html.parser')
        soup = soup.find('table', class_='nfusion-table-border')\
                    .find('tbody')\
                    .find('td', class_='quote-field ask')\
                    .find('span')

        raw_value = soup.text
        value = re.sub(r"\$\s+", "", raw_value)


        grain_value = round((float(value)/15.4324),2)

        file_content = '{"grain_value": '+str(grain_value)+'}'
        print(file_content)

        with open('creativecoin/static/data/grain.json', 'w') as f:
            f.write(file_content)
            
        app.logger.info("Grain value set to: {}".format(grain_value))
    except Exception as e:
        # TODO send notification about error
        app.logger.error("Failed setting grain_value")
    


def run_scheduled_jobs():
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == "true":
        sched = BackgroundScheduler()
        sched.add_job(_run_grain_crawler, trigger='interval', seconds=app.config['GOLD_API_INTERVAL'])
        sched.start()
    

if __name__ == "__main__":
    _run_grain_crawler()