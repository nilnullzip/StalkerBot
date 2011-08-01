#!/usr/bin/env python

import cgitb
cgitb.enable()

import SimpleHTTPServer
import SocketServer
import os, sys
import traceback

sys.path.append("../src")

import commentAndIdToTagSentiment as TS
import logger

logger.log_to_stderr = False

os.chdir("../static")

q = os.environ["QUERY_STRING"]

logger.log ("URL: %s" % (q))

if (q.startswith("userid=")) :
    print "Content-Type: text/html"
    print "Status: 200 OK"
    print

    ignore, userid = q.split('userid=')
    userid = logger.clean_userid(userid)
    if (len(userid)==0) :
        print "[]"
    else :
        logger.log("Stalking: %s" % (userid))
        try :
            print TS.getUserTopicSentiments(userid)
#            raise NameError("Test traceback")
        except :
            logger.log (traceback.format_exc())
            raise
        logger.log("Done stalking: %s" % (userid))
