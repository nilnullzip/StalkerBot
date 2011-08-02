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
        if (live == 1) :
            params = "%s?format=json" % user
            # The following is a site that is surely not a JSON file to throw the error
            #FILE = urllib.urlopen("http://api.ihackernews.com")
            FILE = urllib.urlopen("http://api.ihackernews.com/threads/%s" % params)
            #print "http://api.ihackernews.com/threads/%s" % params
        else :
            filename = "%s.json" % user
            FILE = open (filename, "r")
        comments = []
        for item in json.load(FILE) [u'comments'] :
            comments.append( [str(item[u'postId']), convert( sanitize_html (item[u'comment'])), str(item[u'id'])])
    return comments

#print scrape("pg")
#commentIdStructure = scrape("pg")
#print commentIdStructure
#print len(commentIdStructure)

