#!/usr/bin/python

import json, threading, time, urllib, re
from urlparse import urlparse

#from scrape_juan import scrape
from scrape_juan import scrape as scrape_juan
from scrape_kevin import scrape as scrape_kevin
from tag_generation import generateTags
from effectcheck_api import getSentiment

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
        def __init__ ( self, threadId, comment ):
            self.curThreadId = threadId
            self.curThreadUrl = "http://news.ycombinator.com/item?id=" + self.curThreadId
            self.curComment = comment
            self.curArticleUrl = hnThreadIdToArticleUrl(self.curThreadId)
            threading.Thread.__init__ ( self )
    
        def run ( self ):
            # Sleep before first call in case hacker news was called by scrape (scrape_kevin)
            time.sleep(.05)
            # No need to generate the same tags over and over
            if (not (threadId in threadTagsChecked)):
                threadTags[self.curThreadId] = generateTags(self.curArticleUrl)
                threadTagsChecked.append(self.curThreadId)
            tags = threadTags[self.curThreadId]
            
            sentiment = getSentiment(self.curComment)
            maxSentiments = getMaxSentiments(sentiment)
            for tag in tags:
                tagSentUrlComment.append([tag, maxSentiments, self.curComment, self.curThreadUrl, self.curArticleUrl])
    
    for commentIdElt in commentIdStructure:
        threadId = commentIdElt[0]
        comment = commentIdElt[1]
        # No need to generate the same tags over and over
        if (not (threadId in threadTagsChecked)):
            # Sleep before first call in case hacker news was called by scrape (scrape_kevin)
            time.sleep(.05)
            GetTags ( threadId, comment ).start()
                
    while (threading.active_count() > 1):
        pass
                
    return json.dumps(tagSentUrlComment)
    
def getUserTopicSentiments(userid):
    #print userid
    return commentAndIdToTagSentiment(scrape(userid))

#scrape("dstein64")
#print commentAndIdToTagSentiment(scrape("vijaydev"))
#print commentAndIdToTagSentiment(scrape("dstein64"))
#print commentAndIdToTagSentiment(scrape("melissamiranda"))
#print commentAndIdToTagSentiment(scrape("edw519"))
#print commentAndIdToTagSentiment(scrape("pg"))
