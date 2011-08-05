#!/usr/bin/env python

# Copyright (C) 2011 by Kevin Nam Truong, Daniel Steinberg, Debasish Das, Juan Pineda, Melissa Miranda, and Victoria Pan

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# `THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Authors:
#   Juan Pineda, GitHub: NilNullZip, juan@logician.com

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

def scrape (user) :
    users_url = urllib.urlopen("http://api.thriftdb.com/api.hnsearch.com/users/_search?filter[fields][username]=" + user)
    if (len(json.load(users_url)[u'results']) == 0):
        return None
    
    comments_url = urllib.urlopen("http://api.thriftdb.com/api.hnsearch.com/items/_search?filter[fields][username]=" + user + "&filter[fields][type]=comment&sortby=create_ts%20desc")
                
    comments = []
    for comment in json.load(comments_url) [u'results'] :
        item = comment['item']
        discussion = str(item[u'discussion'])
        if (discussion != "None"):
            comments.append( [str(item[u'discussion'][u'sigid']), str(item[u'discussion'][u'id']), convert( sanitize_html (item[u'text'])), str(item[u'id'])])
#    for comment in comments:
#        print comment
    return comments

#print scrape("pg")
#commentIdStructure = scrape("pg")
#print commentIdStructure
#print len(commentIdStructure)

