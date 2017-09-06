# urban_twitchbot
A simple irc bot for twitch. 
Serves urbandictionary definitions upon request.
Also keeps track of user 'points'.

Edit cfg.py before use.

Requirements:
* python3

About point system:
* points are generated at a rate of 1 per minute
* points are only granted while the streamer is in the channel
* the streamer does not receive points (they would always be #1)
* to prevent other users from receiving points, edit cfg.py
   (this is useful to prevent bots from ranking up)
* !points claim command grants 100 points
* !points claim is only usable while streamer is online

* currently nothing built-in to spend points on. Coming soon.
