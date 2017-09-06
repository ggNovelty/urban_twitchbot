#!/usr/bin/env python3
# cfg.py


HOST = "irc.chat.twitch.tv"
PORT = 6667
NICK = ""        #your twitch username, in quotes
PASS = "oauth:"  #your oauth, in quotes
CHAN = ""        #name of the channel your bot will service, in quotes

RATE = (20/30)
NO_POINTS = [CHAN[1:], "", ""]  #any users you don't want to gain points, 
                                #such as bots. users must be lowercase, 
                                #in quotes, and seperated by a comma.
                                # ** add your bot's name here. **
