# Copyright (C) 2011 by Kevin Nam Truong, Daniel Steinberg, Debasish Das, Juan Pineda, Melissa Miranda, and Victoria Pan

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

import datetime
import sys

logging = True
log_to_stderr = True
log_file_name = "/tmp/StalkerBot.log"

def log (msg) :
    if logging :
        line = "[%s] %s\n" % (datetime.datetime.today(), msg)
        LOG = open (log_file_name, "a")
        LOG.write(line)
        LOG.close()
        if log_to_stderr :
            sys.stderr.write (line)

def clean_userid(u) :
    if len(u) >16 :
        log("userid too long.")
        return "_"
    for c in u :
        if ( not c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-") :
            log("bad character in userid: %s" % (u))
            return "_"
    return u
