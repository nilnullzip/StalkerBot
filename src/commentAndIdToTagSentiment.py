#!/usr/bin/python

import json, threading, time

#from scrape_juan import scrape
from scrape_juan import scrape as scrape_juan
from scrape_kevin import scrape as scrape_kevin
from tag_generation import generateTagsFromThreadId
from effectcheck_api import getSentiment

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
    try:
        commentIdStructure = scrape_juan(userID)
    except ValueError:
        commentIdStructure = scrape_kevin(userID)
    return commentIdStructure

# commentIdStructure is a list of lists. The inner lists contain a String with a ThreadId
# and the second element has the corresponding comment
def commentAndIdToTagSentiment(commentIdStructure):
    tagSentimentOutput = {}
    tagCount = {}
    threadTags = {}
    threadTagsChecked = [] # List for tracking whether for generating a tag was made yet
    
    class GetTags ( threading.Thread ):
        # Override Thread's __init__ method to accept the parameters needed:
        def __init__ ( self, threadId ):
            self.curThreadId = threadId
            threading.Thread.__init__ ( self )
    
        def run ( self ):
            threadTags[self.curThreadId] = generateTagsFromThreadId(self.curThreadId)
            threadTagsChecked.append(self.curThreadId)
            tags = threadTags[self.curThreadId]
            # print for testing
            #print tags
            for tag in tags:
                tagSentimentOutput[tag] = {'Confidence': 0.0, 'Anxiety': 0.0, 'Compassion': 0.0, 'Hostility': 0.0, 'Depression': 0.0, 'Happiness': 0.0}
    
    counter = 0
    for commentIdElt in commentIdStructure:
        # print For testing
        #print commentIdElt
        threadId = commentIdElt[0]
        # No need to generate the same tags over and over
        if (not (threadId in threadTagsChecked)):
            # Sleep before first call in case hacker news was called by scrape (scrape_kevin)
            time.sleep(.05)
            GetTags ( threadId ).start()
            # Now the code always sleeps a bit between requests
            #if (counter >= 5):
            #    # pause requests after every few requests to prevent overloading server
            #    time.sleep(.05)
            #    counter = 0
                
    threadTest = False # Change to True to show thread count
    
    while (threading.active_count() > 1):
        if (threadTest):
            time.sleep(1)
            print "Thread Count: %s" % threading.active_count()
        pass
    
    # tests
    #print "threads 1 done"
    #print threadTags
    #print threadTagsChecked
                
    # Generate tag counts
    for commentIdElt in commentIdStructure:
        threadId = commentIdElt[0]
        tags = threadTags[threadId]
        for tag in tags:
            if tag in tagCount:
                tagCount[tag] = tagCount[tag] + 1
            else:
                tagCount[tag] = 1
    
    for commentIdElt in commentIdStructure:
        threadId = commentIdElt[0]
        tags = threadTags[threadId]
        sentiment = getSentiment(commentIdElt[1])
        for tag in tags:
            for k, s in sentiment.iteritems():
                tagSentimentOutput[tag][k] = tagSentimentOutput[tag][k]+s

    tagAndMaxSentiment = {}
    for tag in tagSentimentOutput:
        tagAndMaxSentiment[tag] = getMaxSentiments(tagSentimentOutput[tag])

    sortedCount = sorted(tagCount.items(), key=lambda x: x[1], reverse=True)

    dictToReturn = []
    for elt in sortedCount:
        dictToReturn.append([elt[0], tagAndMaxSentiment[elt[0]]])
        
    # Future Update: Sort the JSON output by tag appearance
    #print tagCount
    #print json.dumps(dictToReturn)
    return json.dumps(dictToReturn)
    
def getUserTopicSentiments(userid):
    #print userid
    return commentAndIdToTagSentiment(scrape(userid))

#scrape("dstein64")
#print commentAndIdToTagSentiment(scrape("vijaydev"))
#print commentAndIdToTagSentiment(scrape("dstein64"))
#print commentAndIdToTagSentiment(scrape("melissamiranda"))
#print commentAndIdToTagSentiment(scrape("edw519"))
#print commentAndIdToTagSentiment(scrape("pg"))
