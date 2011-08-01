#!/usr/bin/env python

import SimpleHTTPServer
import SocketServer
import os, sys
import commentAndIdToTagSentiment as TS
import logger
import traceback

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

logger.log_to_stderr = True

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(s) :
        logger.log("URL: %s" % (s.path))
        if (s.path.startswith("/cgi-bin/StalkerBotCGI.py?")) :
            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
            ignore, userid = s.path.split('userid=')
            userid = logger.clean_userid(userid)
            if (len(userid)==0) :
                s.wfile.write("[]")
                return
            logger.log("Stalking: %s" % (userid))
            try :
                s.wfile.write(TS.getUserTopicSentiments(userid))
#                raise NameError("Test traceback")
            except:
                logger.log (traceback.format_exc())
                raise
            logger.log("Done stalking: %s" % (userid))
        else :
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(s)
        return

Handler = MyHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "Serving at port:", PORT
print "Use this URL:       http://localhost:%d" % PORT
print "Or to see raw JSON: http://localhost:%d/cgi-bin/StalkerBotCGI.py?userid=pg" % PORT
httpd.serve_forever()
