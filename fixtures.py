import json
import requests
import mydb
from datetime import datetime, date
from queue import Queue
from threading import Thread
import os


class Worker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            season_id, year, league_id = self.queue.get()
            try:
                url = "https://v3.football.api-sports.io/fixtures?league={}&season={}&timezone=Europe/Berlin".format(
                    league_id, year)

                headers = {
                    'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
                    'x-rapidapi-host': 'v3.football.api-sports.io'
                }

                response = requests.get(url=url, headers=headers, timeout=60)
                data = response.json()['response']

                # print(json.dumps(data, indent=4))

                for d in data:
                    match_id = d['fixture']['id']

                    fixture = {'id': match_id, 'date': datetime.fromtimestamp(d['fixture']['timestamp']),
                               'status_long': d['fixture']['status']['long'],
                               'status_short': d['fixture']['status']['short'],
                               'season_id': season_id, 'round': d['league']['round'],
                               'homescore_ht': d['score']['halftime']['home'],
                               'awayscore_ht': d['score']['halftime']['away'],
                               'homescore_ft': d['score']['fulltime']['home'],
                               'awayscore_ft': d['score']['fulltime']['away'],
                               'homescore_et': d['score']['extratime']['home'],
                               'awayscore_et': d['score']['extratime']['away'],
                               'homescore_p': d['score']['penalty']['home'],
                               'awayscore_p': d['score']['penalty']['away'],
                               'hometeam_id': mydb.getTeamToSeason(d['teams']['home']['id'], season_id)[0][0],
                               'awayteam_id': mydb.getTeamToSeason(d['teams']['away']['id'], season_id)[0][0],
                               'slug': d['teams']['home']['name'] + "-" + d['teams']['away']['name'] + "-" + str(
                                   d['fixture']['id'])}

                    print(fixture)
                    mydb.updateFixture(fixture)

                    url = "https://v3.football.api-sports.io/fixtures/statistics?fixture={}".format(match_id)

                    headers = {
                        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
                        'x-rapidapi-host': 'v3.football.api-sports.io'
                    }

                    response = requests.get(url=url, headers=headers, timeout=60)
                    statistics = response.json()['response']

                    # print(json.dumps(statistics, indent=4))

                    if statistics:

                        stats = {'id': match_id}

                        hometeam = statistics[0]['statistics']
                        for t in hometeam:
                            if t['value'] is not None:
                                name = t['type'].replace(' ', '_').replace('%', 'percent').lower() + '_h'
                                if t['type'] == 'Ball Possession' or t['type'] == 'Passes %':
                                    stats[name] = int(t['value'].replace('%', '')) / 100
                                else:
                                    stats[name] = t['value']

                        awayteam = statistics[1]['statistics']
                        for t in awayteam:
                            if t['value'] is not None:
                                name = t['type'].replace(' ', '_').replace('%', 'percent').lower() + '_a'
                                if t['type'] == 'Ball Possession' or t['type'] == 'Passes %':
                                    stats[name] = int(t['value'].replace('%', '')) / 100
                                else:
                                    stats[name] = t['value']

                        print(stats)
                        mydb.updateStats(stats)

            finally:
                self.queue.task_done()


# 1 call per minute for the leagues, teams, fixtures
# who have at least one fixture in progress
# otherwise 1 call per day.
# You can also retrieve all the events of the fixtures in progress
# thanks to the endpoint fixtures?live=all
def fixtures():
    queue = Queue()
    # Create 10 worker threads
    for x in range(1):
        worker = Worker(queue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()

    # Put the tasks into the queue as a tuple
    all_seasons = mydb.getSeasons()
    for season in all_seasons:
        season_id = season[0]
        year = season[1]
        league_id = season[5]

        queue.put((season_id, year, league_id))

    # Causes the main thread to wait for the queue to finish processing all the tasks
    queue.join()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    fixtures()
