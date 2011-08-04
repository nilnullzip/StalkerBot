import datetime
import sys

# Authors:
#   Juan Pineda, GitHub: NilNullZip, juan@logician.com

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
