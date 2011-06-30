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

import datetime
if logging :
    LOG = open ("/tmp/StalkerBot.log", "a")
    LOG.write("[%s] URL: %s\n" % (datetime.datetime.today(), q))
    LOG.flush()

if (q.startswith("userid=")) :
    print "Content-Type: text/html"
    print "Status: 200 OK"
    print

    ignore, userid = q.split('userid=')

    if logging :
        LOG.write("[%s] Stalking: %s\n" % (datetime.datetime.today(), userid))
        LOG.flush()

    print TS.getUserTopicSentiments(userid)
    if logging :
        LOG.write("[%s] Done stalking: %s\n" % (datetime.datetime.today(), userid))
        LOG.flush()

if logging :
    LOG.close()
