import requests
import mydb
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


# 1 call per hour.
def leagues():
    url = "https://v3.football.api-sports.io/status"

    headers = {
        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    response = requests.get(url=url, headers=headers, timeout=60)
    data = response.json()['response']

    current = data['requests']['current']
    limit_day = data['requests']['limit_day']

    if current < limit_day:

        url = 'https://v3.football.api-sports.io/leagues'
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
                    data = response.json()['response']

                    for d in data:
                        league = {'id': d['league']['id'], 'name': d['league']['name'], 'type': d['league']['type'],
                                  'slug': d['league']['name'].replace(' - ', '-').replace('.', '').replace(
                                      ' ', '-').lower()}

                        if d['league']['logo'] is not None:
                            league['logo'] = 'league-logos/{}'.format(d['league']['logo'].split('/')[-1])
                            r = requests.get(d['league']['logo'], allow_redirects=True)
                            open(league['logo'], 'wb').write(r.content)

                        if d['country']['name'] is not None and d['country']['code'] is not None:
                            league['countryid'] = mydb.getCountry(d['country']['name'], d['country']['code'])[0][0]

                        elif d['country']['name'] is not None:
                            league['countryid'] = mydb.getCountry(d['country']['name'])[0][0]

                        # print(json.dumps(d, indent=4))
                        print(league)
                        mydb.updateLeague(league)

                        seasons = d['seasons']
                        for s in seasons:
                            season = {'year': s['year'], 'start': s['start'], 'end': s['end'], 'current': s['current'],
                                      'leagueid': d['league']['id'], 'slug': s['year']}
                            print(season)
                            mydb.updateSeason(season)
    else:
        logging.info("Requests für heute aufgebraucht.")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    leagues()
