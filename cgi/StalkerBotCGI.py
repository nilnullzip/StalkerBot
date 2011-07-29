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

def clean_userid(u) :
    if len(u) >32 :
        log("[%s] userid too long.\n" % (datetime.datetime.today()))
        return ""
    for c in u :
        if ( not c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_") :
            log("[%s] bad character in userid: %s\n" % (datetime.datetime.today(), u))
            return ""
    return u

if (q.startswith("userid=")) :
    print "Content-Type: text/html"
    print "Status: 200 OK"
    print

    ignore, userid = q.split('userid=')
    userid = clean_userid(userid)
    if (len(userid)==0) :
        s.wfile.write("[]")
        return
    log("[%s] Stalking: %s\n" % (datetime.datetime.today(), userid))
    print TS.getUserTopicSentiments(userid)
    log("[%s] Done stalking: %s\n" % (datetime.datetime.today(), userid))
