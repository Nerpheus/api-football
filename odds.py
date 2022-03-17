import json
import requests
import mydb
import os


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

    response = requests.get(url=url, headers=headers, timeout=60)
    current = response.json()['response']['requests']['current']
    limit_day = response.json()['response']['requests']['limit_day']

    if current < limit_day:

        url = "https://v3.football.api-sports.io/odds/mapping"

        headers = {
            'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }

        response = requests.get(url=url, headers=headers, timeout=60).json()

        errors = response['errors']
        # print('Errors:', len(errors))
        if not errors:
            paging = response['paging']['total']
            for page in range(1, paging):
                # print(page, paging)
                url = "https://v3.football.api-sports.io/odds/mapping?page={}".format(page)

                headers = {
                    'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
                    'x-rapidapi-host': 'v3.football.api-sports.io'
                }

                response = requests.get(url=url, headers=headers, timeout=60).json()
                data = response['response']
                # print(json.dumps(data, indent=4))

                if data:
                    match_id = data[0]['fixture']['id']
                    odds(match_id)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    odds_mapping()
