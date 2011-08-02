#!/usr/bin/python

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
DIFFBOT_API_CACHE_UPDATE_THRESHOLD = 604800
SENTIMENT_CACHE_UPDATE_THRESHOLD = 604800
ARTICLE_URL_CACHE_UPDATE_THRESHOLD = 604800
SCRAPED_COMMENTS_CACHE_UPDATE_THRESHOLD = 86400

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
        
def scrapeIdToUrl (threadId):
    url = "http://news.ycombinator.com/item?id=" + threadId
    urlConn = urllib.urlopen(url)
    siteHtml = urlConn.read()
    urlConn.close()
    reg = re.compile('<td class="title"><a href="([^"]*)">')
    regSearch = reg.search(siteHtml)
    if regSearch == None:
        return None
    link = regSearch.group(1)
    # if the link is back to the current page, return None
    return link

def hnApiIdToUrl (threadId):
    params = "%s?format=json" % threadId
    # The following is a site that is surely not a JSON file to throw the error
    #FILE = urllib.urlopen("http://api.ihackernews.com")
    FILE = urllib.urlopen("http://api.ihackernews.com/post/%s" % params)
    url = json.load(FILE)['url']
    return url

# Takes in a Hacker News Thread ID String
def hnThreadIdToArticleUrl( threadId ):
    urlCacheFileStr = ARTICLE_URL_CACHE_DIRECTORY + "/" + threadId
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
        articleUrl = hnApiIdToUrl(threadId)
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
        def __init__ ( self, threadId, comment, commentId, threadIdLock ):
            self.curThreadId = threadId
            self.curThreadUrl = "http://news.ycombinator.com/item?id=" + self.curThreadId
            self.curComment = comment
            self.curCommentId = commentId
            self.threadIdLock = threadIdLock
            threading.Thread.__init__ ( self )
    
        def run ( self ):
            # No need to generate the same tags over and over
            with self.threadIdLock:
                self.curArticleUrl = hnThreadIdToArticleUrl(self.curThreadId)
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
            
            if (self.curThreadId in threadTags):
                tags = threadTags[self.curThreadId]
            
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
            
#            for tag in tags:
#                structForJS = [tag, maxSentiments, self.curComment, self.curThreadUrl, self.curArticleUrl]
#                tagSentUrlComment.append(structForJS)
            structForJS = [tags, maxSentiments, self.curComment, self.curThreadUrl, self.curArticleUrl, self.curArticleTitle, self.curCommentId]
            if (not (None in structForJS)):
                tagSentUrlComment.append(structForJS)
    
    threadList = []
    threadIdLocks = {}
    
    for commentIdElt in commentIdStructure:
        threadId = commentIdElt[0]
        comment = commentIdElt[1]
        commentId = commentIdElt[2]
        if (not (threadId in threadIdLocks)):
            threadIdLocks[threadId] = threading.Lock()
        threadIdLock = threadIdLocks[threadId]
        threadList.append(GetTags ( threadId, comment, commentId, threadIdLock ))
        
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
    
    return commentAndIdToTagSentiment(scrapedComments)

#scrape("dstein64")
#print commentAndIdToTagSentiment(scrape("vijaydev"))
#print scrape("dstein64")
#print commentAndIdToTagSentiment(scrape("melissamiranda"))
#print commentAndIdToTagSentiment(scrape("edw519"))
#print getUserTopicSentiments("dstein64")
