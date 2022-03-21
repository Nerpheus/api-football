import mysql.connector as mc
import os
import time
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def getDatabase():
    # set up database connection
    connection = None
    while not connection:
        try:
            connection = mc.connect(host=os.environ["DB_HOST"],
                                    user=os.environ["DB_USER_2"],
                                    passwd=os.environ["DB_PASSWD_2"],
                                    db="api_football")

        except mc.Error:
            print("Fehler bei der Datenbankverbindung. Versuche es in 30 Sekunden erneut.")
            time.sleep(30)

    return connection


def pushQuery(sql):
    connection = getDatabase()
    cursor = connection.cursor()
    # print(sql)
    try:
        cursor.execute(sql)
        connection.commit()
    except mc.DatabaseError:
        logging.info("fehler bei Abfrage:", sql)
    cursor.close()
    connection.close()


def countFixtures():
    connection = getDatabase()
    cursor = connection.cursor()
    sql = '''SELECT COUNT(*) 
        FROM fixture'''
    cursor.execute(sql)
    fixtures = cursor.fetchone()
    cursor.close()
    connection.close()

    logging.info("Anzahl Fixtures: {}".format(fixtures[0]))


def updateCountry(country):
    columns = ', '.join(country.keys())
    spalten = []
    values = []
    for k, v in country.items():
        if v is not None:
            spalten.append('''{}="{}"'''.format(k, v))
            values.append('''"{}"'''.format(v))
        else:
            spalten.append('''{}=Null'''.format(k))
            values.append('''Null''')

    sql = '''INSERT INTO country ({columns}) 
    VALUES ({values}) 
    ON DUPLICATE KEY UPDATE {spalten}'''.format(
        columns=columns, values=', '.join(values), spalten=", ".join(spalten))
    pushQuery(sql)


def getCountry(name, code2=None):
    connection = getDatabase()
    cursor = connection.cursor()
    sql = '''SELECT * 
    FROM country 
    WHERE name="{}"'''.format(name.replace('-', ' '))
    if code2 is not None:
        sql += ' AND code2="{}"'.format(code2)
    cursor.execute(sql)
    country = cursor.fetchall()
    cursor.close()
    connection.close()

    return country


def getCountries():
    connection = getDatabase()
    cursor = connection.cursor()
    sql = '''SELECT * 
    FROM country'''
    cursor.execute(sql)
    countries = cursor.fetchall()
    cursor.close()
    connection.close()

    return countries


def updateLeague(league):
    columns = ', '.join(league.keys())
    spalten = []
    values = []
    for k, v in league.items():
        if v is not None:
            spalten.append('''{}="{}"'''.format(k, v))
            values.append('''"{}"'''.format(v))
        else:
            spalten.append('''{}=Null'''.format(k))
            values.append('''Null''')

    sql = '''INSERT INTO league ({columns}) 
    VALUES ({values}) 
    ON DUPLICATE KEY UPDATE {spalten}'''.format(
        columns=columns, values=', '.join(values), spalten=", ".join(spalten))
    pushQuery(sql)


def getLeague(leagueid):
    connection = getDatabase()
    cursor = connection.cursor()
    sql = '''SELECT * 
    FROM league 
    WHERE id="{}"'''.format(leagueid)
    cursor.execute(sql)
    country = cursor.fetchall()
    cursor.close()
    connection.close()

    return country


def getSeasons():
    connection = getDatabase()
    cursor = connection.cursor()
    sql = '''SELECT * 
    FROM season
    ORDER BY last_updated, year DESC'''
    cursor.execute(sql)
    seasons = cursor.fetchall()
    cursor.close()
    connection.close()

    return seasons


def updateSeason(season):
    columns = ', '.join(season.keys())
    spalten = []
    values = []
    for k, v in season.items():
        if v is None:
            spalten.append('''{}=Null'''.format(k))
            values.append('''Null''')
        elif v is True:
            spalten.append('''{}=1'''.format(k))
            values.append('''1''')
        elif v is False:
            spalten.append('''{}=0'''.format(k))
            values.append('''0''')
        else:
            spalten.append('''{}="{}"'''.format(k, v))
            values.append('''"{}"'''.format(v))

    sql = '''INSERT INTO season ({columns}) 
    VALUES ({values}) 
    ON DUPLICATE KEY UPDATE {spalten}'''.format(
        columns=columns, values=', '.join(values), spalten=", ".join(spalten))
    
    pushQuery(sql)


def seasonLastUpdated(season_id, date):
    sql = '''UPDATE season SET last_updated="{}" WHERE id="{}"'''.format(date, season_id)

    pushQuery(sql)


def updateTeam(team):
    columns = ', '.join(team.keys())
    spalten = []
    values = []
    for k, v in team.items():
        if v is None:
            spalten.append('''{}=Null'''.format(k))
            values.append('''Null''')
        elif v is True:
            spalten.append('''{}=1'''.format(k))
            values.append('''1''')
        elif v is False:
            spalten.append('''{}=0'''.format(k))
            values.append('''0''')
        else:
            spalten.append('''{}="{}"'''.format(k, v))
            values.append('''"{}"'''.format(v))

    sql = '''INSERT INTO team ({columns}) 
    VALUES ({values}) 
    ON DUPLICATE KEY UPDATE {spalten}'''.format(
        columns=columns, values=', '.join(values), spalten=", ".join(spalten))

    pushQuery(sql)


def updateTeamToSeason(teamtoseason):
    columns = ', '.join(teamtoseason.keys())
    spalten = []
    values = []
    for k, v in teamtoseason.items():
        if v is None:
            spalten.append('''{}=Null'''.format(k))
            values.append('''Null''')
        else:
            spalten.append('''{}="{}"'''.format(k, v))
            values.append('''"{}"'''.format(v))

    sql = '''INSERT INTO teamtoseason ({columns}) 
        VALUES ({values}) 
        ON DUPLICATE KEY UPDATE {spalten}'''.format(
        columns=columns, values=', '.join(values), spalten=", ".join(spalten))

    pushQuery(sql)


def getTeamToSeason(team_id, season_id):
    connection = getDatabase()
    cursor = connection.cursor()
    sql = '''SELECT * 
        FROM teamtoseason 
        WHERE team_id="{}" AND season_id="{}"'''.format(team_id, season_id)
    cursor.execute(sql)
    teamtoseason = cursor.fetchall()
    cursor.close()
    connection.close()

    return teamtoseason


def updateFixture(fixture):
    columns = ', '.join(fixture.keys())
    spalten = []
    values = []
    for k, v in fixture.items():
        if v is None:
            spalten.append('''{}=Null'''.format(k))
            values.append('''Null''')
        else:
            spalten.append('''{}="{}"'''.format(k, v))
            values.append('''"{}"'''.format(v))

    sql = '''INSERT INTO fixture ({columns}) 
            VALUES ({values}) 
            ON DUPLICATE KEY UPDATE {spalten}'''.format(
        columns=columns, values=', '.join(values), spalten=", ".join(spalten))

    pushQuery(sql)


def updateStats(stats):
    columns = ', '.join(stats.keys())
    spalten = []
    values = []
    for k, v in stats.items():
        if v is None:
            spalten.append('''{}=Null'''.format(k))
            values.append('''Null''')
        else:
            spalten.append('''{}="{}"'''.format(k, v))
            values.append('''"{}"'''.format(v))

    sql = '''INSERT INTO stats ({columns}) 
                VALUES ({values}) 
                ON DUPLICATE KEY UPDATE {spalten}'''.format(
        columns=columns, values=', '.join(values), spalten=", ".join(spalten))

    pushQuery(sql)


def updateBookmaker(bookie):
    columns = ', '.join(bookie.keys())
    spalten = []
    values = []
    for k, v in bookie.items():
        if v is None:
            spalten.append('''{}=Null'''.format(k))
            values.append('''Null''')
        else:
            spalten.append('''{}="{}"'''.format(k, v))
            values.append('''"{}"'''.format(v))

    sql = '''INSERT INTO bookmakers ({columns}) 
                    VALUES ({values}) 
                    ON DUPLICATE KEY UPDATE {spalten}'''.format(
        columns=columns, values=', '.join(values), spalten=", ".join(spalten))

    pushQuery(sql)


def updateBets(bet):
    columns = ', '.join(bet.keys())
    spalten = []
    values = []
    for k, v in bet.items():
        if v is None:
            spalten.append('''{}=Null'''.format(k))
            values.append('''Null''')
        else:
            spalten.append('''{}="{}"'''.format(k, v))
            values.append('''"{}"'''.format(v))

    sql = '''INSERT INTO bets ({columns}) 
                        VALUES ({values}) 
                        ON DUPLICATE KEY UPDATE {spalten}'''.format(
        columns=columns, values=', '.join(values), spalten=", ".join(spalten))

    pushQuery(sql)


def updateOdds(quoten):
    columns = ', '.join(quoten.keys())
    spalten = []
    values = []
    for k, v in quoten.items():
        if v is None:
            spalten.append('''{}=Null'''.format(k))
            values.append('''Null''')
        else:
            spalten.append('''{}="{}"'''.format(k, v))
            values.append('''"{}"'''.format(v))

    sql = '''INSERT INTO odds ({columns}) 
                            VALUES ({values}) 
                            ON DUPLICATE KEY UPDATE {spalten}'''.format(
        columns=columns, values=', '.join(values), spalten=", ".join(spalten))

    pushQuery(sql)
