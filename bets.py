import json
import requests
import mydb
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


# 1 call per day.
def bets():
    url = "https://v3.football.api-sports.io/status"

    headers = {
        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    response = requests.get(url=url, headers=headers, timeout=60)
    current = response.json()['response']['requests']['current']
    limit_day = response.json()['response']['requests']['limit_day']

    if current < limit_day:

        url = "https://v3.football.api-sports.io/odds/bets"

        headers = {
            'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }

        retries = 0
        success = False

        while not success and retries <= 5:
            try:
                response = requests.get(url=url, headers=headers, timeout=60)
                success = response.ok
                if success and retries > 0:
                    logging.info("solved!")
            except requests.exceptions.Timeout as timeout:
                wait = retries * 30
                logging.info("Timeout Error! Try again in {} seconds.".format(wait))
                # logging.info(timeout)
                logging.info(response.status_code)
                logging.info(response.json())
                time.sleep(wait)
                retries += 1

        bettings = response.json()['response']

        # print(json.dumps(bookies, indent=4))

        for b in bettings:
            if b['name'] is not None:
                bet = {'id': b['id'], 'name': b['name']}

                print(bet)
                mydb.updateBets(bet)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    bets()
