import json
import requests
import mydb
from datetime import datetime, date
from queue import Queue
from threading import Thread
import os


# 1 call per day.
def countries():
    url = 'https://v3.football.api-sports.io/countries'
    headers = {
        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    response = requests.get(url=url, headers=headers, timeout=1)
    data = response.json()['response']

    for d in data:
        country = {'name': d['name'].replace('-', ' '), 'slug': d['name'].lower()}
        if d['code'] is not None:
            country['code2'] = d['code']

        if d['flag'] is not None:
            country['flag'] = 'country-flags/{}'.format(d['flag'].split('/')[-1])
            r = requests.get(d['flag'], allow_redirects=True)
            open(country['flag'], 'wb').write(r.content)

        # print(country)
        mydb.updateCountry(country)


# 1 call per hour.
def leagues():
    url = 'https://v3.football.api-sports.io/leagues'
    headers = {
        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    response = requests.get(url=url, headers=headers)
    data = response.json()['response']

    for d in data:
        league = {'id': d['league']['id'], 'name': d['league']['name'], 'type': d['league']['type'],
                  'slug': d['league']['name'].replace(' - ', '-').replace('.', '').replace(' ', '-').lower()}

        if d['league']['logo'] is not None:
            league['logo'] = 'league-logos/{}'.format(d['league']['logo'].split('/')[-1])
            r = requests.get(d['league']['logo'], allow_redirects=True)
            open(league['logo'], 'wb').write(r.content)

        if d['country']['name'] is not None and d['country']['code'] is not None:
            league['countryid'] = mydb.getCountry(d['country']['name'], d['country']['code'])[0][0]

        elif d['country']['name'] is not None:
            league['countryid'] = mydb.getCountry(d['country']['name'])[0][0]

        # print(json.dumps(d, indent=4))
        # print(league)
        mydb.updateLeague(league)

        seasons = d['seasons']
        for s in seasons:
            season = {'year': s['year'], 'start': s['start'], 'end': s['end'], 'current': s['current'],
                      'leagueid': d['league']['id'], 'slug': s['year']}
            # print(season)
            mydb.updateSeason(season)

    # print(json.dumps(data, indent=4))


class TeamWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            season_id, year, league_id, country = self.queue.get()
            try:
                url = 'https://v3.football.api-sports.io/teams?league={}&season={}'.format(league_id, year)

                headers = {
                    'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
                    'x-rapidapi-host': 'v3.football.api-sports.io'
                }

                response = requests.get(url=url, headers=headers, timeout=10)
                data = response.json()['response']

                # print(json.dumps(data, indent=4))

                for d in data:
                    team = {'id': d['team']['id'], 'name': d['team']['name'], 'national': d['team']['national'],
                            'countryid': country, 'slug': d['team']['name'].replace(' ', '-').lower()}

                    if d['team']['code'] is not None:
                        team['code'] = d['team']['code']

                    if d['team']['logo'] is not None:
                        team['logo'] = 'team-logos/{}'.format(d['team']['logo'].split('/')[-1])
                        r = requests.get(d['team']['logo'], allow_redirects=True)
                        open(team['logo'], 'wb').write(r.content)

                    teamtoseason = {'season_id': season_id, 'team_id': team['id']}

                    # print(team)
                    mydb.updateTeam(team)
                    mydb.updateTeamToSeason(teamtoseason)

                mydb.seasonLastUpdated(season_id, date.today())

            finally:
                self.queue.task_done()


# 1 call per day.
def teams():
    queue = Queue()
    # Create 10 worker threads
    for x in range(2):
        worker = TeamWorker(queue)
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


# 1 call per minute for the leagues, teams, fixtures
# who have at least one fixture in progress
# otherwise 1 call per day.
# You can also retrieve all the events of the fixtures in progress
# thanks to the endpoint fixtures?live=all
def fixtures():
    seasons = mydb.getSeasons()[:10]
    for season in seasons:
        season_id = season[0]
        year = season[1]
        league_id = season[5]
        url = "https://v3.football.api-sports.io/fixtures?league={}&season={}&timezone=Europe/Berlin".format(
            league_id, year)

        headers = {
            'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }

        response = requests.get(url=url, headers=headers)
        data = response.json()['response']

        # print(json.dumps(data, indent=4))

        for d in data:
            match_id = d['fixture']['id']

            fixture = {'id': match_id, 'date': datetime.fromtimestamp(d['fixture']['timestamp']),
                       'status_long': d['fixture']['status']['long'], 'status_short': d['fixture']['status']['short'],
                       'season_id': season_id, 'round': d['league']['round'],
                       'homescore_ht': d['score']['halftime']['home'], 'awayscore_ht': d['score']['halftime']['away'],
                       'homescore_ft': d['score']['fulltime']['home'], 'awayscore_ft': d['score']['fulltime']['away'],
                       'homescore_et': d['score']['extratime']['home'], 'awayscore_et': d['score']['extratime']['away'],
                       'homescore_p': d['score']['penalty']['home'], 'awayscore_p': d['score']['penalty']['away'],
                       'hometeam_id': mydb.getTeamToSeason(d['teams']['home']['id'], season_id)[0][0],
                       'awayteam_id': mydb.getTeamToSeason(d['teams']['away']['id'], season_id)[0][0],
                       'slug': d['teams']['home']['name'] + "-" + d['teams']['away']['name'] + "-" + str(
                           d['fixture']['id'])}

            # print(fixture)
            mydb.updateFixture(fixture)

            url = "https://v3.football.api-sports.io/fixtures/statistics?fixture={}".format(match_id)

            response = requests.get(url=url, headers=headers)
            statistics = response.json()['response']

            print(json.dumps(statistics, indent=4))

            stats = {'id': match_id}

            hometeam = statistics[0]['statistics']
            for t in hometeam:
                if t['value'] is not None:
                    name = t['type'].replace(' ', '_') + '_h'
                    stats[name] = t['value']

            awayteam = statistics[1]['statistics']
            for t in awayteam:
                if t['value'] is not None:
                    name = t['type'].replace(' ', '_') + '_a'
                    stats[name] = t['value']

            print(stats)


# 1 call per day.
def odds():
    match_id = 719561

    url = "https://v3.football.api-sports.io/odds?fixture={}".format(match_id)

    headers = {
        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    response = requests.get(url=url, headers=headers)
    odd = response.json()['response']

    print(json.dumps(odd, indent=4))


# 1 call per day.
def players():
    pass


# 1 call per minute for the fixtures in progress
# otherwise 1 call per day.
# You can also retrieve all the events of the fixtures in progress
# thanks to the endpoint fixtures?live=all
def events():
    match_id = 718252

    url = "https://v3.football.api-sports.io/fixtures/events?fixture={}".format(match_id)

    headers = {
        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    response = requests.get(url=url, headers=headers)
    event = response.json()['response']

    print(json.dumps(event, indent=4))


# 1 call every 15 minutes for the fixtures in progress
# otherwise 1 call per day.
def lineups():
    pass


# 1 call every minute for the fixtures in progress
# otherwise 1 call per day.
def player_stats():
    pass


def test():
    season_id = 3271
    year = 2021
    league = 159
    country = mydb.getLeague(league)[0][2]

    url = 'https://v3.football.api-sports.io/teams?league={}&season={}'.format(league, year)

    headers = {
        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    response = requests.get(url=url, headers=headers)
    data = response.json()['response']

    # print(json.dumps(data, indent=4))

    for d in data:
        team = {'id': d['team']['id'], 'name': d['team']['name'], 'national': d['team']['national'],
                'countryid': country, 'slug': d['team']['name'].replace(' ', '-').lower()}

        if d['team']['code'] is not None:
            team['code'] = d['team']['code']

        if d['team']['logo'] is not None:
            team['logo'] = 'team-logos/{}'.format(d['team']['logo'].split('/')[-1])
            r = requests.get(d['team']['logo'], allow_redirects=True)
            open(team['logo'], 'wb').write(r.content)

        teamtoseason = {'season_id': season_id, 'team_id': team['id']}

        # print(team)
        mydb.updateTeam(team)
        mydb.updateTeamToSeason(teamtoseason)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    countries()
    leagues()
    teams()
    # fixtures()
    # events()
    # odds()
    # test()
