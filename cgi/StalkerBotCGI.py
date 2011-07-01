#!/usr/bin/env python

import cgitb
cgitb.enable()

import SimpleHTTPServer
import SocketServer
import os, sys

sys.path.append("../src")

import commentAndIdToTagSentiment as TS

os.chdir("../static")

q = os.environ["QUERY_STRING"]

logging = True

def log (msg) :
    if logging :
        LOG = open ("/tmp/StalkerBot.log", "a")
        LOG.write(msg)
        LOG.close()
    
import datetime
log ("[%s] URL: %s\n" % (datetime.datetime.today(), q))

if (q.startswith("userid=")) :
    print "Content-Type: text/html"
    print "Status: 200 OK"
    print

    ignore, userid = q.split('userid=')
    log("[%s] Stalking: %s\n" % (datetime.datetime.today(), userid))
    print TS.getUserTopicSentiments(userid)
    log("[%s] Done stalking: %s\n" % (datetime.datetime.today(), userid))
