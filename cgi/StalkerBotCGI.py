#!/usr/bin/env python

import cgitb
cgitb.enable()

import SimpleHTTPServer
import SocketServer
import os, sys
import commentAndIdToTagSentiment as TS
#from commentAndIdToTagSentiment import commentAndIdToTagSentiment as TS

os.chdir("../static")

#print s.path
#if (s.path.startswith("/stalk?userid=")) :
if ((not os.environ["QUERY_STRING"].startswith("userid=")) and False) :
    sys.exit(0)
else :
#if (False) :
    #s.send_response(200)
    #print "Date: Tue, 28 Jun 2011 09:24:44 GMT"
    #print "Expires: -1"
    #print "Cache-Control: private, max-age=0"
#    print "HTTP/1.0 200 OK"
    print "Content-Type: text/html"
    print "Status: 200 OK"
    print
    #print "<html>"
    #print "<center>Hello, Linux.com!</center>"
    #print "</html>"

    q = os.environ["QUERY_STRING"]
#    print "QUERY=%s" % q
#            s.wfile.write('[["Rock and roll", ["Confidence", "Anxiety", "Compassion", "Hostility", "Depression", "Happiness"]]]')
    ignore, userid = q.split('userid=')
 #   print "ignoring %s" % ignore
 #   print "Stalking: %s" % userid
    print TS.getUserTopicSentiments(userid)
 #   print "Done stalking."
