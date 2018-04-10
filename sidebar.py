import urllib
import json
import praw
import pytz
import conf
from datetime import datetime

r = praw.Reddit(client_id=conf.settings['client_id'],
       client_secret=conf.settings['client_secret'],
       password=conf.settings['password'],
       username=conf.settings['username'],
       user_agent=conf.settings['user_agent'])
sub = r.subreddit('thunder')
mod = sub.mod
settings = mod.settings()
sidebar_contents = settings['description']

BOLD = "**"
PIPE = " | "

TEAMID = "1610612760"
TEAMNAME = "Oklahoma City"

utc = pytz.timezone('UTC')

nbaBoxScoreBaseUrl = "https://stats.nba.com/game/"

def get_important_links():
    return """### **Important links**
* [Rules](https://www.reddit.com/r/Thunder/wiki/rules)
* [Message the mods](https://www.reddit.com/message/compose?to=%2Fr%2FThunder)
* [Thunder Twitter](https://twitter.com/okcthunder)
* [Thunder Facebook](https://www.facebook.com/OKCThunder)
* [/r/nba](https://www.reddit.com/r/nba)
    """

def get_schedule():
    obs = read_json("http://data.nba.net/prod/v1/2017/teams/" + TEAMID + "/schedule.json")
    month = datetime.strftime(datetime.today(), '%b')
    eastern = pytz.timezone('US/Central')

    schedule = """Date | Team | Location | Result
    -|-|-|-|-
    """

    games = obs["league"]["standard"]
    for game in games:
        if game["seasonStageId"] > 1:
            gameDate = game["startTimeUTC"]
            dt = datetime.strptime(gameDate, '%Y-%m-%dT%H:%M:%S.%fZ')
            utc_dt = datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, tzinfo=utc)
            local_date = utc_dt.astimezone(eastern)
            gameMonth = datetime.strftime(local_date, '%b')
            gameDay = datetime.strftime(local_date, '%d')
            gameHour = datetime.strftime(local_date, '%I')
            gameMinute = datetime.strftime(local_date, '%M')
            gameTime = gameHour + ":" + gameMinute
            gameTime = gameTime.lstrip("0").replace(" 0", " ")

            if month == gameMonth:
                homeScore = game["hTeam"]["score"]
                awayScore = game["vTeam"]["score"]

                date = gameMonth + " " + gameDay
                if game["isHomeTeam"]:
                    location = "HOME"
                    team = get_team_by_id(game["vTeam"]["teamId"])
                    if not (homeScore == ""):
                        if int(homeScore) > int(awayScore):
                            result = "[" + BOLD + "W" + BOLD + " "
                        else:
                            result = "[" + BOLD + "L" + BOLD + " "
                        result = result + awayScore + " - " + BOLD + homeScore + BOLD + "](https://stats.nba.com/game/" + game["gameId"] + ")"
                else:
                    location = "AWAY"
                    team = get_team_by_id(game["hTeam"]["teamId"])
                    if not (homeScore == ""):
                        if int(homeScore) > int(awayScore):
                            result = "[" + BOLD + "L" + BOLD + " "
                        else:
                            result = "[" + BOLD + "W" + BOLD + " "
                        result = result + BOLD + awayScore + BOLD + " - " + homeScore + "](https://stats.nba.com/game/" + game["gameId"] + ")"

                if homeScore == "":
                    result = str(gameTime) + " PM"

                schedule = schedule + date + PIPE + city_name_to_hrefs(team) + PIPE + location + PIPE + result + "\n"

    return schedule


def get_roster():
    return """
    No | Name | Pos. | College
    -|-|-|-
    0 | R. Westbrook | G | UCLA
    2 | R. Felton | G | N. Carolina
    3 | C. Brewer | G/F | Florida
    4 | N. Collison | F | Kansas
    7 | C. Anthony | F | Syracuse
    8 | A. Abrines | G | *Spain*
    9 | J. Grant | F | Syracuse
    12 | S. Adams | C | Pittsburgh
    13 | P. George | F | Fresno State
    15 | K. Singler | F | Duke
    23 | T. Ferguson | G | Adelaide 36ers
    21 | A. Roberson | G/F | Colorado
    34 | J. Huestis | F | Stanford
    44 | D. Johnson | C | Kentucky
    54 | P. Patterson | F | Kentucky
    """

def get_standings():
    obs = read_json("http://data.nba.com/json/cms/2017/standings/conference.json")

    standings = """|#|TEAM|W|L|PCT|GB
|-|-|-|-|-|-|
    """

    for i in range(0, 15):
        west = obs["sports_content"]["standings"]["conferences"]["West"]["team"][i]
        stats = west["team_stats"]
        rank = stats["rank"]
        name = west["name"]
        nickname = west["nickname"]
        wins = stats["wins"]
        losses = stats["losses"]
        gb = stats["gb_conf"]
        pct = stats["pct"]
        pct = pct[1:]

        if name == TEAMNAME:
            rank = BOLD + rank + BOLD
            nickname = BOLD + nickname + BOLD
            wins = BOLD + wins + BOLD
            losses = BOLD + losses + BOLD
            gb = BOLD + gb + BOLD
            pct = BOLD + pct + BOLD

        standings = standings + rank + PIPE + city_name_to_hrefs(name) + " " + nickname + PIPE + wins + PIPE + losses + PIPE + pct + PIPE + gb + "\n"

    return standings

def get_team_by_id(id):
    obs = read_json("http://data.nba.net/prod/v1/2017/teams.json")
    teams = obs["league"]["standard"]
    id = str(id)

    for team in teams:
        if team["teamId"] == id:
            return team["fullName"]

def read_json(url):
    req = urllib.urlopen(url).read()
    return json.loads(req)

def city_name_to_hrefs(var_string):
    city_names_to_hrefs = var_string

    #List of NBA city names
    city_names = ['Boston', 'Brooklyn', 'New York', 'Philadelphia', 'Toronto',
                  'Chicago', 'Cleveland', 'Detroit', 'Indiana', 'Milwaukee',
                  'Atlanta', 'Charlotte', 'Miami', 'Orlando', 'Washington',
                  'Golden State', 'Golden St', 'LA Clippers', 'L.A. Lakers', 'Los Angeles Clippers',
                  'Los Angeles Lakers', 'Phoenix', 'Sacramento', 'Dallas', 'Houston',
                  'Memphis', 'New Orleans', 'San Antonio', 'Denver', 'Minnesota',
                  'Oklahoma City', 'Portland', 'Philadelphia', 'Utah'
                 ]
    #Corresponding list of hrefs
    hrefs = ['[](/r/bostonceltics)', '[](/r/gonets)', '[](/r/nyknicks)', '[](/r/sixers)', '[](/r/torontoraptors)',
             '[](/r/chicagobulls)', '[](/r/clevelandcavs)', '[](/r/detroitpistons)', '[](/r/pacers)', '[](/r/mkebucks)',
             '[](/r/atlantahawks)', '[](/r/charlottehornets)', '[](/r/heat)', '[](/r/orlandomagic)', '[](/r/washingtonwizards)',
             '[](/r/warriors)', '[](/r/warriors)', '[](/r/laclippers)', '[](/r/lakers)', '[](/r/laclippers)',
             '[](/r/lakers)', '[](/r/suns)', '[](/r/kings)', '[](/r/mavericks)', '[](/r/rockets)',
             '[](/r/memphisgrizzlies)', '[](/r/nolapelicans)', '[](/r/nbaspurs)', '[](/r/denvernuggets)', '[](/r/timberwolves)',
             '[](/r/thunder)', '[](/r/ripcity)', '[](/r/sixers)', '[](/r/utahjazz)'
            ]
    #Go through the lists
    for city, href in zip(city_names, hrefs):
        #Replace all of the city names with hrefs
        city_names_to_hrefs = city_names_to_hrefs.replace(city, href)
    return city_names_to_hrefs

def get_current_time():
    return datetime.now()

def build_sidebar():
    sidebar = ""
    important_links = get_important_links()
    schedule = get_schedule()
    roster = get_roster()
    standings = get_standings()
    current_time = str(get_current_time())
    month = str(get_current_time().strftime("%B")).upper()

    sidebar = sidebar + important_links
    sidebar = sidebar + "\n###THUNDER " + month + " SCHEDULE\n"
    sidebar = sidebar + schedule
    sidebar = sidebar + "\n###WESTERN CONFERENCE STANDINGS\n"
    sidebar = sidebar + standings
    sidebar = sidebar + "\n###THUNDER ROSTER\n"
    sidebar = sidebar + roster

    mod.update(description=sidebar)

build_sidebar()
