# urban_twitchbot
A simple irc bot for twitch. 
Serves urbandictionary definitions upon request.
Also keeps track of user 'points'.

Edit cfg.py before use.

Requirements:
* Written with Python3 on Linux, untested on other machines.
* Requires an account on twitch.tv.

About point system:
* points are generated at a rate of 1 per minute
* points are only granted while the streamer is in the channel
* the streamer does not receive points (they would always be #1)
* to prevent other users from receiving points, edit cfg.py
   (this is useful to prevent bots from ranking up)
* !points claim command grants 100 points
* !points claim is only usable while streamer is online

* currently nothing built-in to spend points on. Coming soon.

Optional:
I have included make-run.sh, a script which checks running processes
for an instance of 'bot.py'. If bot.py is not found, (bot isn't running), 
the script will launch bot.py at the given location. We can set this 
script to be run automatically using a cron job.

To set the cron job:
Type 'crontab -e' without quotes into the terminal.
Create a new line at the bottom of the document.
Enter the following on the new line:

`* * * * * /home/pi/Desktop/make-run.sh > /dev/null 2>&1`

This will run your 'make-run.sh' script once per minute, every minute.
You may have to edit the middle segment of this line, depending on 
where your make-run.sh file is stored.

More optional cron:
Add the following on a new line of your crontab (crontab -e).
This script will kill the bot.py process every day at 11am.
If you have the cron job provided above, the bot will start right back up.

`0 11 * * * kill -9 $(ps ax | grep 'bot.py' | grep -v grep | awk '{ print $1 }')`

Final optional cron:
Here is an optional cron job to reboot your raspberry pi, once per week.
Instead of putting this in your normal crontab (crontab -e), put this
line in your superuser crontab (sudo crontab -e).
This cron job will reboot the pi every monday at 8am.

`0 8 * * 1 /sbin/shutdown -r now`
