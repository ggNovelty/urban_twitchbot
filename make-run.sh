#!/bin/bash
#make-run.sh
#makes sure a process is always running

process=bot.py
#full directory of your script, in quotes.
makerun="/home/pi/Desktop/projects/python/bots/urban_twitchbot/bot.py"

if ps ax | grep -v grep | grep $process > /dev/null
then
  exit
else
  python3 $makerun &
fi

exit
