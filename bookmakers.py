import json
import requests
import mydb
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


# 1 call per day.
def bookmakers():
    url = "https://v3.football.api-sports.io/status"

    headers = {
        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    data = False
    while not data:
        response = requests.get(url=url, headers=headers, timeout=60)
        data = response.json()['response']

    current = data['requests']['current']
    limit_day = data['requests']['limit_day']

    if current < limit_day:

        url = "https://v3.football.api-sports.io/odds/bookmakers"

        headers = {
            'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }

        retries = 1
        success = False

        while not success and retries <= 5:
            try:
                response = requests.get(url=url, headers=headers, timeout=60)
                success = response.ok
                if success and retries > 1:
                    logging.info("solved!")
            except requests.exceptions.Timeout:
                wait = retries * 30
                logging.info("Timeout Error! Try again in {} seconds.".format(wait))
                time.sleep(wait)
                retries += 1
            else:
                errors = response.json()['errors']
                if not errors:
                    bookies = response.json()['response']

                    for b in bookies:
                        bookie = {'id': b['id'], 'name': b['name']}

                        print(bookie)
                        mydb.updateBookmaker(bookie)
    else:
        logging.info("Requests für heute aufgebraucht.")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    bookmakers()
