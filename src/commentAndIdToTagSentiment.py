#!/usr/bin/python

import json, threading, time, urllib, re, os
from urlparse import urlparse

#from scrape_juan import scrape
from scrape_juan import scrape as scrape_juan
from scrape_kevin import scrape as scrape_kevin
from tag_generation import generateTags
from effectcheck_api import getSentiment

TAG_CACHE_DIRECTORY = "../cache/tags"
SENTIMENT_CACHE_DIRECTORY = "../cache/sentiments"

# Takes in a Hacker News Thread ID String
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
        def __init__ ( self, threadId, comment, commentId ):
            self.curThreadId = threadId
            self.curThreadUrl = "http://news.ycombinator.com/item?id=" + self.curThreadId
            self.curComment = comment
            self.curArticleUrl = hnThreadIdToArticleUrl(self.curThreadId)
            self.curCommentId = commentId
            threading.Thread.__init__ ( self )
    
        def run ( self ):
            if (self.curArticleUrl != None):
                # No need to generate the same tags over and over
                if (not (threadId in threadTagsChecked)):
                    threadTagsChecked.append(self.curThreadId)
                    tagCacheFileStr = TAG_CACHE_DIRECTORY + "/" + urllib.quote(self.curThreadId,'')
                    if (os.path.isfile(tagCacheFileStr)):
                        cache = open(tagCacheFileStr, "r")
                        threadTags[self.curThreadId] = json.loads(cache.read())
                    else:
                        # Sleep before call in case hacker news was called prior
                        time.sleep(.05)
                        threadTags[self.curThreadId] = generateTags(self.curArticleUrl)
                        # Cache article tags
                        cache = open(tagCacheFileStr, "w")
                        cache.write(json.dumps(threadTags[self.curThreadId]))
                    cache.close()
                else:
                    # Wait until the tags are added for the threadId by some other thread call
                    while (not (self.curThreadId in threadTags)):
                        pass
                    
                tags = threadTags[self.curThreadId]
                
                sentCacheFileStr = SENTIMENT_CACHE_DIRECTORY + "/" + urllib.quote(self.curCommentId,'')
                if (os.path.isfile(sentCacheFileStr)):
                    cache = open(sentCacheFileStr, "r")
                    maxSentiments = json.loads(cache.read())
                else:
                    sentiment = getSentiment(self.curComment)
                    maxSentiments = getMaxSentiments(sentiment)
                    # Cache max sentiments
                    cache = open(sentCacheFileStr, "w")
                    cache.write(json.dumps(maxSentiments))
                
                for tag in tags:
                    structForJS = [tag, maxSentiments, self.curComment, self.curThreadUrl, self.curArticleUrl]
                    tagSentUrlComment.append(structForJS)
    
    for commentIdElt in commentIdStructure:
        threadId = commentIdElt[0]
        comment = commentIdElt[1]
        commentId = commentIdElt[2]
        GetTags ( threadId, comment, commentId ).start()
                
    while (threading.active_count() > 1):
        pass
                
    return json.dumps(tagSentUrlComment)

def getUserTopicSentiments(userid):
    return commentAndIdToTagSentiment(scrape(userid))

#scrape("dstein64")
#print commentAndIdToTagSentiment(scrape("vijaydev"))
#print scrape("dstein64")
#print commentAndIdToTagSentiment(scrape("melissamiranda"))
#print commentAndIdToTagSentiment(scrape("edw519"))
#print commentAndIdToTagSentiment(scrape("pg"))
