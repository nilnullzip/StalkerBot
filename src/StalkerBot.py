#!/usr/bin/env python

import SimpleHTTPServer
import SocketServer
import os, sys
import commentAndIdToTagSentiment as TS

from optparse import OptionParser

parser = OptionParser()

parser.add_option("-p", "--port", dest="port", type="int",
                  help="listen on port", metavar="PORT")

#parser.add_option("-e", "--test-error",
#                  action="store_true", dest="test-error", default=False,
#                  help="Pass error condition to HTML")

(options, args) = parser.parse_args()

if args != [] :
    parser.print_help()
    sys.exit()

if options.port==None :
    PORT = 8000
else:
    PORT = options.port

os.chdir("../static")

logging = True

def log (msg) :
    if logging :
        LOG = open ("../StalkerBot.log", "a")
        LOG.write(msg)
        LOG.close()
        sys.stderr.write (msg)

import datetime

def clean_userid(u) :
    if len(u) >32 :
        log("[%s] userid too long.\n" % (datetime.datetime.today()))
        return ""
    for c in u :
        if ( not c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_") :
            log("[%s] bad character in userid: %s\n" % (datetime.datetime.today(), u))
            return ""
    return u

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(s) :
        log("[%s] URL: %s\n" % (datetime.datetime.today(), s.path))
#        if (s.path.startswith("/cgi-bin/StalkerBotCGI.py?userid=")) :
        if (s.path.startswith("/cgi-bin/StalkerBotCGI.py?")) :
            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
            ignore, userid = s.path.split('userid=')
            userid = clean_userid(userid)
            if (len(userid)==0) :
                s.wfile.write("[]")
                return
            log("[%s] Stalking: %s\n" % (datetime.datetime.today(), userid))
            s.wfile.write(TS.getUserTopicSentiments(userid))
            log("[%s] Done stalking: %s\n" % (datetime.datetime.today(), userid))
        else :
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(s)
        return

Handler = MyHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "Serving at port:", PORT
print "Use this URL:       http://localhost:%d" % PORT
print "Or to see raw JSON: http://localhost:%d/cgi-bin/StalkerBotCGI.py?userid=pg" % PORT
httpd.serve_forever()
