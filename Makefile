.SILENT:

help:
	echo "make N       -- show number of queries in log"
	echo "make Nunique -- show number of unique queries in log"
	echo "make queries -- list (unique) queries"
	echo "make pg      -- show number if queries for user pg"
	echo "make log     -- real time log display"
	echo "make flush   -- flush cache"
	echo "make clean   -- clean up temporary files"
	echo "make setup   -- setup new installation"
	echo "make start   -- start or restart apache server"
	echo "make update  -- update server from GitHub"
	echo "make push    -- push local changes to GitHub"

N :
	cat /tmp/StalkerBot.log | grep Stalking\: | colrm 1 39 | wc -l

Nunique :
	cat /tmp/StalkerBot.log | grep Stalking\: | colrm 1 39 | sort | uniq | wc -l

queries :
	cat /tmp/StalkerBot.log | grep Stalking\: | colrm 1 39 | sort | uniq

pg :
	cat /tmp/StalkerBot.log | grep Stalking\: | colrm 1 39 | grep pg | wc -l

log :
	tail -n 100 -f /tmp/StalkerBot.log

flush :
	rm -r /var/tmp/stalkerbot-cache

clean :
	rm -f *~
	rm -f */*~
	rm -f */*.pyc
setup :
	mkdir -p options-and-settings/api-keys/
	echo "make sure to copy key files to options-and-settings/api-keys/"

start :
	/etc/init.d/apache2 restart

update :
	cd /srv/www/htdocs/StalkerBot/
	pwd
	git pull --rebase

push :
	echo "To push changes to Github use \"git push --tags\""
