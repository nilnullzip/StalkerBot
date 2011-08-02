.SILENT:

help:
	echo "make N       -- show number of queries in log"
	echo "make Nunique -- show number of unique queries in log"
	echo "make queries -- list (unique) queries"
	echo "make pg      -- show number if queries for user pg"
	echo "make log     -- real time log display"
	echo "make flush   -- flush cache"

N :
	cat /tmp/StalkerBot.log | grep Stalking\: | colrm 1 39 | wc -l

Nunique :
	cat /tmp/StalkerBot.log | grep Stalking\: | colrm 1 39 | sort | uniq | wc -l

queries :
	cat /tmp/StalkerBot.log | grep Stalking\: | colrm 1 39 | sort | uniq

pg :
	cat /tmp/StalkerBot.log | grep Stalking\: | colrm 1 39 | grep pg | wc -l

log :
	tail -f /tmp/StalkerBot.log

flush :
	rm -r /var/tmp/stalkerbot-cache

clean :
	rm -f *~
	rm -f */*~
	rm -f */*.pyc
