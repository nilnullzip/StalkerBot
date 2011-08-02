#!/usr/bin/env python

import json
import pprint
import sys
import urllib

from BeautifulSoup import BeautifulSoup

VALID_TAGS = []

def sanitize_html(value):

    soup = BeautifulSoup(value)

    for tag in soup.findAll(True):
        if tag.name not in VALID_TAGS:
            tag.hidden = True

    return soup.renderContents()

import copy, re

hexentityMassage = [(re.compile('&#x([^;]+);'), 
    lambda m: '&#%d' % int(m.group(1), 16))]

def convert(html):
    return BeautifulSoup(html,
        convertEntities=BeautifulSoup.HTML_ENTITIES,
        markupMassage=hexentityMassage).contents[0].string

live = 1 # set to 1 to fetch user data live vs. from test file

def scrape (auser) :
    userlist = [auser]

    for user in userlist :
        # The following is a site that is surely not a JSON file to throw the error
        #FILE = urllib.urlopen("http://api.ihackernews.com")
        FILE = urllib.urlopen("http://api.thriftdb.com/api.hnsearch.com/items/_search?filter[fields][username]=" + user + "&filter[fields][type]=comment&sortby=create_ts%20desc")
                    
        comments = []
        for comment in json.load(FILE) [u'results'] :
            item = comment['item']
            discussion = str(item[u'discussion'])
            if (discussion != "None"):
                comments.append( [str(item[u'discussion'][u'id']), convert( sanitize_html (item[u'text'])), str(item[u'id'])])
    return comments

#print scrape("pg")
#commentIdStructure = scrape("pg")
#print commentIdStructure
#print len(commentIdStructure)

