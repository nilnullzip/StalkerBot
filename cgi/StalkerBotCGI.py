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

import datetime
LOG = open ("../log.txt", "a")
LOG.write("[%s] URL: %s\n" % (datetime.datetime.today(), q))

if (q.startswith("userid=")) :
    print "Content-Type: text/html"
    print "Status: 200 OK"
    print

    ignore, userid = q.split('userid=')

    LOG.write("[%s] Stalking: %s\n" % (datetime.datetime.today(), userid))
    print TS.getUserTopicSentiments(userid)
    LOG.write("[%s] Done stalking: %s\n" % (datetime.datetime.today(), userid))

LOG.close()
