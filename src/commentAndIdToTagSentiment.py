#!/usr/bin/python

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

import json, threading, time, datetime, urllib, re, os, tempfile

from scrape_kevin import scrape as scrape_kevin
from scrape_juan import scrape as scrape_juan
from tag_generation import articleApiRequest
from effectcheck_api import getSentiment
from read_key import readKey

# Determines whether caching is on or off
CACHE_ON = True
BASE_CACHE_DIRECTORY = "/var/tmp"

# Check for user specified BASE_CACHE_DIRECTORY in ../custom-cache-dir file
# Relative references (.. and .) should be relative to the src folder, although
# the file is in one level higher
if (os.path.isfile("../options-and-settings/custom-cache-dir")):
    BASE_CACHE_DIRECTORY = open("../options-and-settings/custom-cache-dir", "r").readline().rstrip('\n').rstrip('\r')
    
# Raise exception if BASE_CACHE_DIRECTORY does not exist
if not os.path.exists(BASE_CACHE_DIRECTORY):
    raise IOError("BASE_CACHE_DIRECTORY " + BASE_CACHE_DIRECTORY + " must exist")

DIFFBOT_API_CACHE_DIRECTORY = BASE_CACHE_DIRECTORY + "/stalkerbot-cache/diffbot-api"
SENTIMENT_CACHE_DIRECTORY = BASE_CACHE_DIRECTORY + "/stalkerbot-cache/sentiments"
ARTICLE_URL_CACHE_DIRECTORY = BASE_CACHE_DIRECTORY + "/stalkerbot-cache/article-urls"
SCRAPED_COMMENTS_CACHE_DIRECTORY = BASE_CACHE_DIRECTORY + "/stalkerbot-cache/scraped-comment-data"

# Number of seconds for which cached data will be reused
# There are 86,400 seconds in a day and 604,800 seconds in a week
DIFFBOT_API_CACHE_UPDATE_THRESHOLD = 10
SENTIMENT_CACHE_UPDATE_THRESHOLD = 10
ARTICLE_URL_CACHE_UPDATE_THRESHOLD = 10
SCRAPED_COMMENTS_CACHE_UPDATE_THRESHOLD = 10

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

def hnApiIdToUrl (sigId):
    FILE = urllib.urlopen("http://api.thriftdb.com/api.hnsearch.com/items/%s" % sigId)
    json_load = json.load(FILE)
    url = json_load['url']
    if (url == None):
        url = "http://news.ycombinator.com/item?id=" + str(json_load['id'])
    return url

# Takes in a Hacker News Thread ID String
def hnThreadIdToArticleUrl( sigId ):
    urlCacheFileStr = ARTICLE_URL_CACHE_DIRECTORY + "/" + sigId
    urlCacheLoaded = False
    if (CACHE_ON):
        ensure_dir(urlCacheFileStr)
        if os.path.isfile(urlCacheFileStr):
            urlCacheFileAge = time.time() - os.path.getmtime(urlCacheFileStr)
            if urlCacheFileAge < ARTICLE_URL_CACHE_UPDATE_THRESHOLD:
                cache = open(urlCacheFileStr, "r")
                articleUrl = json.loads(cache.read())
                urlCacheLoaded = True
    if not urlCacheLoaded:
        articleUrl = hnApiIdToUrl(sigId)
        if (CACHE_ON):
            # Cache
            cache = open(urlCacheFileStr, "w")
        else:
            cache = tempfile.TemporaryFile()
        cache.write(json.dumps(articleUrl))
    cache.close()
    return articleUrl    

def getMaxSentiments(sentimentDict):
    maximum = 0
    maxElts = []
    for k, s in sentimentDict.iteritems():
        if s > maximum:
            maximum = s
    for k, s in sentimentDict.iteritems():
        if s == maximum:
            maxElts.append(k)
    return maxElts

def scrape(userID):
    # Use scrape_kevin since http://api.ihackernews.com/ is not working (6/30/2011)
    return scrape_juan(userID)

# commentIdStructure is a list of lists. The inner lists contain a String with a ThreadId
# and the second element has the corresponding comment
def commentAndIdToTagSentiment(commentIdStructure):
    threadTags = {}
    threadTitles = {}
    threadTagsChecked = [] # List for tracking whether for generating a tag was made yet
    tagSentUrlComment = []
    diffbotApiKey = readKey("diffbot-article-api")
    effectCheckApiKey = readKey("effectcheck")
    if (not diffbotApiKey):
        raise Exception("Must specify a Diffbot article API key")
    if (not diffbotApiKey):
        raise Exception("Must specify an EffectCheck API key")
    
    class GetTags ( threading.Thread ):
        # Override Thread's __init__ method to accept the parameters needed:
        def __init__ ( self, sigId, threadId, comment, commentId, threadIdLock ):
            self.sigId = sigId
            self.curThreadId = threadId
            self.curThreadUrl = "http://news.ycombinator.com/item?id=" + self.curThreadId
            self.curComment = comment
            self.curCommentId = commentId
            self.threadIdLock = threadIdLock
            threading.Thread.__init__ ( self )
    
        def run ( self ):
            # No need to generate the same tags over and over
            with self.threadIdLock:
                self.curArticleUrl = hnThreadIdToArticleUrl(self.sigId)
                if self.curArticleUrl == None:
                    return
                else:
                    if (not (self.curThreadId in threadTagsChecked)):
                        threadTagsChecked.append(self.curThreadId)
                        tagCacheFileStr = DIFFBOT_API_CACHE_DIRECTORY + "/" + self.curThreadId
                        tagCacheLoaded = False
                        if (CACHE_ON):
                            ensure_dir(tagCacheFileStr)
                            if os.path.isfile(tagCacheFileStr):
                                tagCacheFileAge = time.time() - os.path.getmtime(tagCacheFileStr)
                                if tagCacheFileAge < DIFFBOT_API_CACHE_UPDATE_THRESHOLD:
                                    cache = open(tagCacheFileStr, "r")
                                    apiResponseFromCache = json.loads(cache.read())
                                    tagCacheLoaded = True
                                    if (('tags' in apiResponseFromCache) and (apiResponseFromCache['tags'] != [])):
                                        threadTags[self.curThreadId] = apiResponseFromCache['tags']
                                    else:
                                        threadTags[self.curThreadId] = None
                                    if ('title' in apiResponseFromCache):
                                        threadTitles[self.curThreadId] = apiResponseFromCache['title']
                                    else:
                                        threadTitles[self.curThreadId] = None
                        if not tagCacheLoaded:
                            # Sleep before call in case hacker news was called prior
                            time.sleep(.05)
                            apiResponse = articleApiRequest(self.curArticleUrl, diffbotApiKey)
                            if (('tags' in apiResponse) and (apiResponse['tags'] != [])):
                                threadTags[self.curThreadId] = apiResponse['tags']
                            else:
                                threadTags[self.curThreadId] = None
                            if ('title' in apiResponse):
                                threadTitles[self.curThreadId] = apiResponse['title']
                            else:
                                threadTitles[self.curThreadId] = None
                            if (CACHE_ON):
                                # Cache article tags
                                cache = open(tagCacheFileStr, "w")
                            else:
                                cache = tempfile.TemporaryFile()
                            cache.write(json.dumps(apiResponse))
                        cache.close()
                        
            self.curArticleTitle = threadTitles[self.curThreadId]
            # If thread title is missing, use URL
            if (self.curArticleTitle == None):
                self.curArticleTitle = self.curArticleUrl
            
            if (self.curThreadId in threadTags):
                tags = threadTags[self.curThreadId]
            # If tags missing, use empty list
            if (tags == None):
                tags = []
            
            sentCacheFileStr = SENTIMENT_CACHE_DIRECTORY + "/" + self.curCommentId
            sentCacheLoaded = False
            if (CACHE_ON):
                ensure_dir(sentCacheFileStr)
                if os.path.isfile(sentCacheFileStr):
                    sentCacheFileAge = time.time() - os.path.getmtime(sentCacheFileStr)
                    if sentCacheFileAge < SENTIMENT_CACHE_UPDATE_THRESHOLD:
                        cache = open(sentCacheFileStr, "r")
                        maxSentiments = json.loads(cache.read())
                        sentCacheLoaded = True
            if not sentCacheLoaded:
                sentiment = getSentiment(self.curComment, effectCheckApiKey)
                maxSentiments = getMaxSentiments(sentiment)
                if (CACHE_ON):
                    # Cache max sentiments
                    cache = open(sentCacheFileStr, "w")
                else:
                    cache = tempfile.TemporaryFile()
                cache.write(json.dumps(maxSentiments))
            cache.close()
            
            structForJS = [tags, maxSentiments, self.curComment, self.curThreadUrl, self.curArticleUrl, self.curArticleTitle, self.curCommentId]
            if (not (None in structForJS)):
                tagSentUrlComment.append(structForJS)
    
    threadList = []
    threadIdLocks = {}
    
    for commentIdElt in commentIdStructure:
        sigId = commentIdElt[0]
        threadId = commentIdElt[1]
        comment = commentIdElt[2]
        commentId = commentIdElt[3]
        if (not (threadId in threadIdLocks)):
            threadIdLocks[threadId] = threading.Lock()
        threadIdLock = threadIdLocks[threadId]
        threadList.append(GetTags ( sigId, threadId, comment, commentId, threadIdLock ))
        
    # Start Threads
    for thread in threadList:
        thread.start()
    
    # Wait for threads to finish      
    for thread in threadList: 
        thread.join()
                
    return json.dumps(tagSentUrlComment)

def getUserTopicSentiments(userid):
    scrapedCommentsCacheFileStr = SCRAPED_COMMENTS_CACHE_DIRECTORY + "/" + userid
    scrapedCommentsCacheLoaded = False
    if (CACHE_ON):
        ensure_dir(scrapedCommentsCacheFileStr)
        if os.path.isfile(scrapedCommentsCacheFileStr):
            scrapedCommentsCacheFileAge = time.time() - os.path.getmtime(scrapedCommentsCacheFileStr)
            if scrapedCommentsCacheFileAge < SCRAPED_COMMENTS_CACHE_UPDATE_THRESHOLD:
                cache = open(scrapedCommentsCacheFileStr, "r")
                scrapedComments = json.loads(cache.read())
                scrapedCommentsCacheLoaded = True
    if not scrapedCommentsCacheLoaded:
        scrapedComments = scrape(userid)
        if (CACHE_ON):
            # Cache
            cache = open(scrapedCommentsCacheFileStr, "w")
        else:
            cache = tempfile.TemporaryFile()
        cache.write(json.dumps(scrapedComments))
    cache.close()
    
    if scrapedComments == None :
        return None
    else :
        return commentAndIdToTagSentiment(scrapedComments)

#scrape("dstein64")
#print commentAndIdToTagSentiment(scrape("vijaydev"))
#print scrape("dstein64")
#print commentAndIdToTagSentiment(scrape("melissamiranda"))
#print commentAndIdToTagSentiment(scrape("edw519"))
#print getUserTopicSentiments("dstein64")
