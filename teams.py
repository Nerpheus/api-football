import requests
import mydb
from datetime import date, datetime
from queue import Queue
from threading import Thread
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def oneSeason(season_id, year, league_id, country):
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

        url = 'https://v3.football.api-sports.io/teams?league={}&season={}'.format(league_id, year)

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

        data = response.json()['response']

        # print(json.dumps(data, indent=4))

        for d in data:
            team = {'id': d['team']['id'], 'name': d['team']['name'], 'national': d['team']['national'],
                    'countryid': country, 'slug': d['team']['name'].replace(' ', '-').lower()}

            if d['team']['code'] is not None:
                team['code'] = d['team']['code']

            if d['team']['logo'] is not None:
                team['logo'] = '/home/nico/api-football/team-logos/{}'.format(d['team']['logo'].split('/')[-1])
                r = requests.get(d['team']['logo'], allow_redirects=True)
                open(team['logo'], 'wb').write(r.content)

            teamtoseason = {'season_id': season_id, 'team_id': team['id']}

            print(team)
            mydb.updateTeam(team)
            mydb.updateTeamToSeason(teamtoseason)


# 1 call per day.
class Worker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            season_id, year, league_id, country = self.queue.get()
            try:
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

                    url = 'https://v3.football.api-sports.io/teams?league={}&season={}'.format(league_id, year)

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

                    data = response.json()['response']

                    # print(json.dumps(data, indent=4))

                    for d in data:
                        team = {'id': d['team']['id'], 'name': d['team']['name'], 'national': d['team']['national'],
                                'countryid': country, 'slug': d['team']['name'].replace(' ', '-').lower()}

                        if d['team']['code'] is not None:
                            team['code'] = d['team']['code']

                        if d['team']['logo'] is not None:
                            team['logo'] = '/home/nico/api-football/team-logos/{}'.format(d['team']['logo'].split('/')[-1])
                            r = requests.get(d['team']['logo'], allow_redirects=True)
                            open(team['logo'], 'wb').write(r.content)

                        teamtoseason = {'season_id': season_id, 'team_id': team['id']}

                        print(team)
                        mydb.updateTeam(team)
                        mydb.updateTeamToSeason(teamtoseason)

            finally:
                self.queue.task_done()


def teams():
    queue = Queue()
    # Create 10 worker threads
    for x in range(10):
        worker = Worker(queue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()

    # Put the tasks into the queue as a tuple
    all_seasons = mydb.getSeasons()
    for season in all_seasons:
        # print(season)
        season_id = season[0]
        year = season[1]
        league_id = season[5]
        country = mydb.getLeague(league_id)[0][2]

        queue.put((season_id, year, league_id, country))

    # Causes the main thread to wait for the queue to finish processing all the tasks
    queue.join()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    teams()
