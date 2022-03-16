import requests
import mydb
import os


# 1 call per day.
def countries():
    url = 'https://v3.football.api-sports.io/countries'
    headers = {
        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    response = requests.get(url=url, headers=headers, timeout=60)
    data = response.json()['response']

    for d in data:
        country = {'name': d['name'].replace('-', ' '), 'slug': d['name'].lower()}
        if d['code'] is not None:
            country['code2'] = d['code']

        if d['flag'] is not None:
            country['flag'] = 'country-flags/{}'.format(d['flag'].split('/')[-1])
            r = requests.get(d['flag'], allow_redirects=True)
            open(country['flag'], 'wb').write(r.content)

        print(country)
        mydb.updateCountry(country)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    countries()
