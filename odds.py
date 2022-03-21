import json
import requests
import mydb
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


# 1 call per day.
def odds(match_id):
    url = "https://v3.football.api-sports.io/odds?fixture={}".format(match_id)

    headers = {
        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    response = requests.get(url=url, headers=headers, timeout=60)

    data = response.json()['response']

    if data:
        bookies = data[0]['bookmakers']

        for bookie in bookies:
            bookmaker_id = bookie['id']
            bets = bookie['bets']
            for bet in bets:
                bet_id = bet['id']
                values = bet['values']
                for v in values:
                    quoten = {'match_id': match_id, 'bookmaker_id': bookmaker_id, 'bet_id': bet_id, 'value': v['value'],
                              'odd': v['odd']}

                    print(quoten)
                    mydb.updateOdds(quoten)

                # print(json.dumps(bets, indent=4))


# 1 call per day.
def odds_mapping():
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

        url = "https://v3.football.api-sports.io/odds/mapping"

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
                    paging = response.json()['paging']['total']
                    for page in range(1, paging):
                        # print(page, paging)
                        url = "https://v3.football.api-sports.io/odds/mapping?page={}".format(page)

                        headers = {
                            'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
                            'x-rapidapi-host': 'v3.football.api-sports.io'
                        }

                        response = requests.get(url=url, headers=headers, timeout=60).json()
                        matches = response['response']
                        # print(json.dumps(data, indent=4))

                        if data:
                            match_id = matches[0]['fixture']['id']
                            odds(match_id)
    else:
        logging.info("Requests für heute aufgebraucht.")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    odds_mapping()
