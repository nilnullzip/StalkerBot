#!/usr/bin/python

import json, threading, time, datetime, urllib, re, os, tempfile

from scrape_kevin import scrape as scrape_kevin
from tag_generation import generateTags
from effectcheck_api import getSentiment

# Determines whether caching is on or off
CACHE_ON = True

TAG_CACHE_DIRECTORY = "../cache/tags"
SENTIMENT_CACHE_DIRECTORY = "../cache/sentiments"
ARTICLE_URL_CACHE_DIRECTORY = "../cache/article-urls"
SCRAPED_COMMENTS_CACHE_DIRECTORY = "../cache/scraped-comment-data"

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

# Takes in a Hacker News Thread ID String
def hnThreadIdToArticleUrl( threadId ):
    urlCacheFileStr = ARTICLE_URL_CACHE_DIRECTORY + "/" + threadId
    if (CACHE_ON):
        ensure_dir(urlCacheFileStr)
    if (CACHE_ON and os.path.isfile(urlCacheFileStr)):
        cache = open(urlCacheFileStr, "r")
        articleUrl = json.loads(cache.read())
    else:
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
        if link == "item?id=" + threadId:
            articleUrl = None
        else:
            articleUrl = link
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
    return scrape_kevin(userID)

# commentIdStructure is a list of lists. The inner lists contain a String with a ThreadId
# and the second element has the corresponding comment
def commentAndIdToTagSentiment(commentIdStructure):
    threadTags = {}
    threadTagsChecked = [] # List for tracking whether for generating a tag was made yet
    tagSentUrlComment = []
    
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
                        tagCacheFileStr = TAG_CACHE_DIRECTORY + "/" + self.curThreadId
                        if (CACHE_ON):
                            ensure_dir(tagCacheFileStr)
                        if (CACHE_ON and os.path.isfile(tagCacheFileStr)):
                            cache = open(tagCacheFileStr, "r")
                            threadTags[self.curThreadId] = json.loads(cache.read())
                        else:
                            # Sleep before call in case hacker news was called prior
                            time.sleep(.05)
                            threadTags[self.curThreadId] = generateTags(self.curArticleUrl)
                            if (CACHE_ON):
                                # Cache article tags
                                cache = open(tagCacheFileStr, "w")
                            else:
                                cache = tempfile.TemporaryFile()
                            cache.write(json.dumps(threadTags[self.curThreadId]))
                        cache.close()
            
            tags = threadTags[self.curThreadId]
            
            sentCacheFileStr = SENTIMENT_CACHE_DIRECTORY + "/" + self.curCommentId
            if (CACHE_ON):
                ensure_dir(sentCacheFileStr)
            if (CACHE_ON and os.path.isfile(sentCacheFileStr)):
                cache = open(sentCacheFileStr, "r")
                maxSentiments = json.loads(cache.read())
            else:
                sentiment = getSentiment(self.curComment)
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
            structForJS = [tags, maxSentiments, self.curComment, self.curThreadUrl, self.curArticleUrl]
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
    # Only scrape once per day
    today = datetime.date.today()
    todaystr = today.isoformat()

    scrapedCommentsCacheFileStr = SCRAPED_COMMENTS_CACHE_DIRECTORY + "/" + todaystr + "/" + userid
    if (CACHE_ON):
        ensure_dir(scrapedCommentsCacheFileStr)
    
    if (CACHE_ON and os.path.isfile(scrapedCommentsCacheFileStr)):
        cache = open(scrapedCommentsCacheFileStr, "r")
        scrapedComments = json.loads(cache.read())
    else:
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
