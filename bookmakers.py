import json
import requests
import mydb
import os


# 1 call per day.
def bookmakers():
    url = "https://v3.football.api-sports.io/odds/bookmakers"

    headers = {
        'x-rapidapi-key': os.environ["API_FOOTBALL_KEY"],
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    response = requests.get(url=url, headers=headers, timeout=60)
    bookies = response.json()['response']

    # print(json.dumps(bookies, indent=4))

    for b in bookies:
        bookie = {'id': b['id'], 'name': b['name']}

        print(bookie)
        mydb.updateBookmaker(bookie)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    bookmakers()
