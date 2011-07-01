#!/usr/bin/env python

import SimpleHTTPServer
import SocketServer
import os, sys
import commentAndIdToTagSentiment as TS
#from commentAndIdToTagSentiment import commentAndIdToTagSentiment as TS

if (len(sys.argv)!=2):
    PORT = 8000
else:
    PORT = int(sys.argv[1])

os.chdir("../static")

logging = True

def log (msg) :
    if logging :
        LOG = open ("../StalkerBot.log", "a")
        LOG.write(msg)
        LOG.close()
        sys.stderr.write (msg)

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(s) :
        import datetime
        log("[%s] URL: %s\n" % (datetime.datetime.today(), s.path))
        if (s.path.startswith("/cgi-bin/StalkerBotCGI.py?userid=")) :
            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
            ignore, userid = s.path.split('userid=')
            log("[%s] Stalking: %s\n" % (datetime.datetime.today(), userid))
            s.wfile.write(TS.getUserTopicSentiments(userid))
            log("[%s] Done stalking: %s\n" % (datetime.datetime.today(), userid))
        else :
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(s)
        return

Handler = MyHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "serving at port", PORT
httpd.serve_forever()
