#!/usr/bin/env python

#Copyright (C) 2011 by Kevin Nam Truong, Daniel Steinberg, Debasish Das, Juan Pineda, Melissa Miranda, and Victoria Pan
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# `THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Authors:
#   Juan Pineda, GitHub: NilNullZip, juan@logician.com

import cgitb
#cgitb.enable()

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
