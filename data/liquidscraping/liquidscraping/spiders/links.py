# getting the data
import requests
from urllib.request import urlopen
from lxml import etree  # get html from site and write to local file
import re

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
    return l
if __name__ == '__main__':

url = 'https://liquipedia.net/starcraft2/Premier_Tournaments'

# read local html file and set up lxml html parser
response = urlopen(url)
htmlparser = etree.HTMLParser()
tree = etree.parse(response, htmlparser)

# got it. This takes all elements in the tables and restricts it to only the ones that reference a tournament page.
# Now we have a framework to implement on all 7 of our starting links. which will happen with a simple loop.

