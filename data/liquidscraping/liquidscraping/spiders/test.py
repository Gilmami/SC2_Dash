# getting the data
import requests
from urllib.request import urlopen
from lxml import etree  # get html from site and write to local file
import re

url = 'https://liquipedia.net/starcraft2/Premier_Tournaments'
headers = {'Content-Type': 'text/html', }
response = requests.get(url, headers=headers)
html = response.text
with open('sc2', 'w') as f:
    f.write(html)

# read local html file and set up lxml html parser
response = urlopen(url)
htmlparser = etree.HTMLParser()
tree = etree.parse(response, htmlparser)

# looking for a number of about 200 links in my list
# Using these resources:
# https://towardsdatascience.com/how-to-use-python-and-xpath-to-scrape-websites-99eaed73f1dd
# https://www.w3schools.com/xml/xpath_axes.asp
# https://www.oreilly.com/library/view/xpath-and-xpointer/0596002912/ch04.html
# I think i should restrict my domain to the body of the site, not the whole site.

obj = tree.xpath('//table/tbody/tr/td/a')

links = etree.ElementTree()

for i in range(0, len(obj)):
    if "class" in obj[i].attrib:
        del obj[i]
    elif len(re.split(r'\s', obj[i].text)) > 2:
        del obj[i]
    else:
        continue
