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

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(s) :
        print s.path
        if (s.path.startswith("/cgi-bin/StalkerBotCGI.py?userid=")) :
            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
            ignore, userid = s.path.split('userid=')
            print "Stalking: %s" % userid
            s.wfile.write(TS.getUserTopicSentiments(userid))
            print "Done stalking."
        else :
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(s)
        return

Handler = MyHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "serving at port", PORT
httpd.serve_forever()
