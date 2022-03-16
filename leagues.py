import requests
import mydb
import os


# 1 call per hour.
def leagues():
    url = 'https://v3.football.api-sports.io/leagues'
    headers = {
        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    response = requests.get(url=url, headers=headers, timeout=60)
    data = response.json()['response']

    for d in data:
        league = {'id': d['league']['id'], 'name': d['league']['name'], 'type': d['league']['type'],
                  'slug': d['league']['name'].replace(' - ', '-').replace('.', '').replace(' ', '-').lower()}

        if d['league']['logo'] is not None:
            league['logo'] = 'home/nico/api-football/league-logos/{}'.format(d['league']['logo'].split('/')[-1])
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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    leagues()
