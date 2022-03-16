import json
import requests
import mydb
import os


def bets():
    url = "https://v3.football.api-sports.io/odds/bets"

    headers = {
        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    response = requests.get(url=url, headers=headers, timeout=60)
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
