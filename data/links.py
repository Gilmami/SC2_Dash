# getting the data
import requests
from urllib.request import urlopen
from lxml import etree  # get html from site and write to local file
import re
import time
import psycopg2
from psycopg2 import sql

#I'm not sure I need this level of abstraction. might be over complicating things.
# I think this is probably the best way to go for ease when porting into the database
class tournament:
    def __init__(self, name, matches, patch=None):
        self.matches = matches
        self.name = name
        self.patch = patch


#extracts the specific child tournament links for future manipulation
def liquidlinkextraction(url):
    response = urlopen(url)
    htmlparser = etree.HTMLParser()
    tree = etree.parse(response, htmlparser)
    l= list()
    for elem in tree.findall('//table/tbody/tr/td/a'):
        if "class" in elem.attrib:
            continue
        elif elem.text is None:
            continue
        elif len(re.split(r'\s', elem.text)) < 2:
            continue
        else:
            l.append(elem)

    j = list()
    for elem in l:
        j.append("https://liquipedia.net" + elem.get("href"))

    return j

# this takes specific tournament links and extracts the matchup data as a list of dicts. only for premier and major
# events for minor and below they use a bracket object that I have yet to parse.

def dataextraction(url):
    response = urlopen(url)
    htmlparser = etree.HTMLParser()
    tree = etree.parse(response, htmlparser)

    tname = tree.findall("//h1")[0][0].text
    # gonna ignore the patch for now and naively (read: conveniently) analyze as if all patches are the same.
    matchtree = tree.findall("//table/tbody/tr[@class='match-row']/td")
    count = 0
    matchups = list()

    for elem in matchtree:
        if count % 4 == 0:
            match = {}
            match["player1"] = elem.getchildren()[0].text
            match["player1race"] = elem.getchildren()[1].get("title")

        elif count % 4 == 1:
            try:
                match["player1score"] = int(elem.text)
            except ValueError:
                if elem.text == "-":
                    match["player1score"] = "N/A"
            finally:
                pass

        elif count % 4 == 2:
            try:
                match["player2score"] = int(elem.text)
            except ValueError:
                if elem.text == "-":
                    match["player2score"] = "N/A"
            finally:
                pass

        elif count % 4 == 3:
            match["player2"] = elem.getchildren()[1].text
            match["player2race"] = elem.getchildren()[0].get("title")
            matchups.append(match)

        count += 1
    tourn = tournament(tname, matchups)
        # first elem in list = row object, therefore needs to be processed elem by elem.
        # every 4th elem starting at 0 is laid out matchtree[0].getchildren()[0].text is the name of the player,
        # matchtree[0].getchildren()[1].get("title") is the race.
        # every 4th elem starting at 1 is the player falling on 0, 4, 8 ...'s result in the matchup.
        # every 4th elem starting at 2 is the player falling on 3, 7, 11..'s result in the matchup.
        # every 4th elem starting at 3: matchtree[3].getchildren()[0].get("title") gets the race.
        # if the class of an elem is 'matchlistslot bg-win', that's the winner of the matchup.
        # matchtree[3].getchildren()[1].text is the player name.
        # now I need to figure out how I want to format the data that will allow for ease of comparision.
        # each matchup is one person vs another person. they have a name, race, and outcome and happened on a specific
        # version of the game, which I'll have to pull differently and tag onto the front of the list of dicts.

        # I could make it a list of dicts, with the first element being the version of the game like ("version #",
        # {Player1 : player1, Player2 : player2, Player1race : 'Zerg', player2race : 'Protoss', player1score : 2,
        # player2score : 1}, {.....}, ... ) where each dict object represents a matchup.
    return tourn

if __name__ == '__main__':

# got it. This takes all elements in the tables and restricts it to only the ones that reference a tournament page
# (mostly)
# Now we have a framework to implement on all 7 of our starting links. which will happen with a simple loop.

    initial = ["https://liquipedia.net/starcraft2/Premier_Tournaments",
           "https://liquipedia.net/starcraft2/Major_Tournaments",
           "https://liquipedia.net/starcraft2/Minor_Tournaments",
           "https://liquipedia.net/starcraft2/Monthly_Tournaments",
           "https://liquipedia.net/starcraft2/Weekly_Tournaments",
           "https://liquipedia.net/starcraft2/Show_Matches",
           "https://liquipedia.net/starcraft2/Female_Tournaments"]

# not sure how I want to do this yet, so i'm just gonna leave it alone for today.
tourneys = list()
for i in initial:
    links = liquidlinkextraction(i)
    time.sleep(10)
    for link in links:
        tourneys.append(dataextraction(link))
        time.sleep(10)

# i don't want to get banned from scraping liquipedia so i haven't done this yet, I was hoping to build more out
# before I do this just in case I do get banned from scraping, it might also be a good excersize to see if I can
# actually implement the things I want to do.


tourneys = list()
links = liquidlinkextraction("https://liquipedia.net/starcraft2/Premier_Tournaments")
for link in links:
    tourneys.append(dataextraction(link))
    time.sleep(10)

# tourneys is now a list of lists of dicts... what disgusting beast have I created?
# now I need to take this list of list of dicts and parse it into a much easier setup.
# I feel like putting this essentially raw into a database would be the easiest way
# to pull it in a somewhat usable format, since we don't really care about the specific matches,
# but instead the history between two players. So it would help to be able to compare quickly the large
# volume of data I have in matchups. Pretty sure it's close to like, 16,000 individual matchups.

# now to figure out how to actually get tourney into a database... Here goes.
# first I gotta establish the connection with the database and create the table that my matchup data will go into
# This will, in the future be more of like, an initialization step for the application? but for now,
# but for now, this is where i'm gonna put it. (I really hope i'm not making spaghetti code rn...)

# Now I have my queries all set up, I need to figure out how to iterate through my names and take any that have
# numeric at the front of the name and put them into the back, because 2020_gsl_masters is the same to me as
# _gsl_masters_2020. Okay, from names need to clean -, /, (, ), " ", :, and they have to start with a non-numeric.
# FUUUU. such a pain.



connection = psycopg2.connect("dbname=matchdata user=michaelgilman")
cursor = connection.cursor()

for i in tourneys:
    cursor.execute(
        sql.SQL("""CREATE TABLE {} (player1 text, player1race text, player1score integer,
           player2score integer, player2 text, 
           player2race text);""".format(i.name.replace(" ", "_").replace(":", "").replace(".","").replace("-","").replace("/","").replace("20", "Twenty").lower())))

for i in tourneys:
    for match in i.matches:
        cursor.execute(
            sql.SQL("""INSERT INTO {} (player1, player1race, player1score, player2score, player2, player2race)
                       VALUES (%(player1)s, %(player1race)s, %(player1score)s, %(player2score)s, %(player2)s, 
                       %(player2race)s);""".format(i.name.replace(" ", "_").replace(":", "").replace("20", "twenty").lower())), match)
