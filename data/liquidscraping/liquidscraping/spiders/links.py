# getting the data
import requests
from urllib.request import urlopen
from lxml import etree  # get html from site and write to local file
import re
import time

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

def dataextraction(url):
    response = urlopen(url)
    htmlparser = etree.HTMLParser()
    tree = etree.parse(response, htmlparser)

    matchtree = tree.findall("//table/tbody/tr[@class='match-row']/td")
    count = 0
    matchups = list()


    for elem in matchtree:
        if count % 4 == 0:
            match = {}
            match["player1"] = elem.getchildren()[0].text
            match["player1race"] = elem.getchildren()[1].get("title")
        elif count % 4 == 1:
            match["player1score"] = int(elem.text)
        elif count % 4 == 2:
            match["player2score"] = int(elem.text)
        elif count % 4 == 3:
            match["player2"] = elem.getchildren()[1].text
            match["player2race"] = elem.getchildren()[0].get("title")
            matchups.append(match)

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
        #
    return matchups

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
# for i in initial:
#     links = liquidlinkextraction(i)
#
# for link in links:
#     dataextraction(link)