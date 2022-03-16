import json
import requests
import mydb
from datetime import datetime, date
from queue import Queue
from threading import Thread
import os


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

    response = requests.get(url=url, headers=headers, timeout=60)
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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    events()
