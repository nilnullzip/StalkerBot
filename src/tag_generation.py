#!/usr/bin/python

import urllib2
import json

import sys, urllib, re
from urlparse import urlparse

# Takes in a Hacker News Thread ID String
# 
def hnThreadIdToArticleUrl( threadId ):
    url = "http://news.ycombinator.com/item?id=" + threadId
    urlConn = urllib.urlopen(url)
    siteHtml = urlConn.read()
    urlConn.close()
    reg = re.compile('<td class="title"><a href="([^"]*)">')
    regSearch = reg.search(siteHtml)
    if regSearch == None:
        return None
    link = regSearch.group(1)
    parsedLink = urlparse(link)
    # if the link is back to the current page, return None
    if link == "item?id=" + threadId:
        return None
    else:
        return link

def generateTags( url ):
    tag_list = []
    if url==None: 
        return tag_list
    api_base = 'http://www.diffbot.com/api/article?token=f1affaf273f1bf567b85de4106c4af5b&url='
    api_key = api_base + url + '&tags'
    #print 'api key : ' + api_key
    req = urllib2.Request(api_key)
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        return []
    
    json_response = response.read()
    objs = json.loads(json_response)
    tag_exists = False
    for o in objs:
        if o == 'tags':
            tag_exists = True 
    if tag_exists:
        for o in objs ['tags']:
            tag_list.append(o)
    return tag_list

def generateTagsFromThreadId( threadId ):
    url = hnThreadIdToArticleUrl(threadId)
    tags = generateTags(url)
    return tags

def test():
    # Test out your program
    # 2082625 is a poll thread
    tag_list = generateTagsFromThreadId( "2082625" )
    print 'poll thread'
    for i in tag_list:
        print i
    
    # 2696937 is a link
    tag_list =  generateTagsFromThreadId( "2696937" )
    print 'link'
    for i in tag_list:
        print i
    
    # 2654788 is a tell HN
    tag_list = generateTagsFromThreadId( "2654788" )
    print 'tell HN'
    for i in tag_list:
        print i
    
    tag_list = generateTagsFromThreadId( "2696207" )
    print '4th test'
    for i in tag_list:
        print i
    
    url = 'http://www.huffingtonpost.com/2011/03/04/frozen-smoke-energy-storage_n_830894.html'
    print 'url used : ' + url
    tag_list = generateTags(url)
    print 'Test for tag generation'
    for i in tag_list:
        print i
