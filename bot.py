#!/usr/bin/env python3
# bot.py

#TODO: Spend points?

import cfg

import logging
import os
import re
import requests
import shelve
import socket
import sys
import threading

from time import sleep
from datetime import datetime, timedelta
from urllib.parse import quote


#regex, pulls chat from twitch irc 'response'.
chat_msg=re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

#regex, tries to extract an urbandictionary word's definition.
#definition_regex = r'.definition.\:(.+?)(permalink.\:|author.\: ..|current_vot|thumbs_up.\:|thumbs_down|example.\:..|word.\:.....|defid.\:....)'


def chat(sock, msg):
    sock.send(bytes("PRIVMSG {} :{} \r\n".format(cfg.CHAN, msg), 'utf-8'))

def urban(word):

    word_in_ascii = quote(word)
    built_url = 'https://api.urbandictionary.com/v0/define?term=' + word_in_ascii

    r = requests.get(built_url)

    if len(r.json()['list']) > 0:

        top_definition = r.json()['list'][0]['definition']

        top_definition = re.sub(r'\r', ' ', top_definition)
        top_definition = re.sub(r'\n', ' ', top_definition)
        top_definition = re.sub(r'   ', ' ', top_definition)

        bot_says = word + '- ' + top_definition
        if len(bot_says) >= 500:
            bot_says = bot_says[:499]

        return bot_says

    else:

        bot_says = word + ' is undefined!'

        return bot_says

def chatbot():
    while True:
        response = irc.recv(1204).decode('utf-8')

        username = re.search(r"\w+", response).group(0)
        message = chat_msg.sub("", response)
        message = message.rstrip()
        #logging.debug('  '+ username + ": " + message)


        if response == "PING :tmi.twitch.tv\r\n":
            irc.send(bytes("PONG :tmi.twitch.tv\r\n", 'utf-8'))

        else:
            if re.match(r'^!urban', message):

                bot_says = "i'm confused.. what did you ask?"

                if (message == '!urban') or (message == '!urban '):
                    bot_says = "!urban - defines a word using urban dictionary."

                else:
                    search_term = message[7:]
                    bot_says = urban(search_term)

                chat(irc, bot_says)

            elif re.match(r'^!commands', message):

                bot_says = 'commands: !urban word - gives the urban ' \
                         + 'definition of a word (if it exists). '\
                         + '!points help - commands for !points. '

                chat(irc, bot_says)

            elif re.match(r'^!bots', message):

                bot_says = 'MrDestructoid'
            
                chat(irc, bot_says)
            
            elif re.match(r'^!points', message):

                if (message == '!points') or (message == '!points '):
                    with shelve.open(os.path.join(sys.path[0],cfg.CHAN[1:])) as s:
                        if username in s:
                            user_points = str(s[username])
                            bot_says = '@' + username + ' has ' \
                                    + user_points \
                                    + ' points.'

                        else:
                            bot_says = ('@' + username \
                                    + ' you got no points, '\
                                    + 'watch more stream bruh.')

                    chat(irc, bot_says)
                
                elif message == '!points help':
                    bot_says = '@' + username + ' :' + '!points commands: ' \
                             + "'!points', '!points claim' " \
                             + "'!points top'. points cannot be earned while"\
                             + " streamer is offline."

                    chat(irc, bot_says)

                elif message == '!points claim':
                    redeemed_filename = cfg.CHAN[1:] + 'REDEEMED'

                    current_users = requests.get(\
                                    'https://tmi.twitch.tv/group/user/'\
                                  + cfg.CHAN[1:] + '/chatters')
                    current_users = current_users.json()
                    current_users = current_users['chatters']['moderators']\
	                          + current_users['chatters']['viewers']

                    if cfg.CHAN[1:] in current_users:
                        with shelve.open(os.path.join(sys.path[0],redeemed_filename)) as redeemed:
                            if username in redeemed:
                                bot_says = '@'+username+' you may only claim '\
                                         + 'points once per stream.'
                            else:
                                with shelve.open(os.path.join(sys.path[0],cfg.CHAN[1:])) as s:
                                    if username in s:
                                        s[username] += 100
                                        bot_says = '@'+username+' claimed 100'\
                                                 + ' points. new_total: '\
                                                 + str(s[username])
                                    else:
                                        s[username] = 100
                                        bot_says = '@'+username+' claimed 100'\
                                                 + ' points. new_total: '\
                                                 + str(s[username])

                                redeemed[username] = 1
                                        
                    else:
                        bot_says = cfg.CHAN[1:] + ' must be online to claim,'\
                                 + ' check back later.'

                    chat(irc, bot_says)

                elif message == '!points top':
                    try:
                        with shelve.open(os.path.join(sys.path[0],cfg.CHAN[1:])) as s:
                            score_tups = sorted(s.items(), key=lambda x: \
                                                  x[1])[::-1]
                            top_five = score_tups[:5]

                            bot_says = '!points high scores: ' \
                    +'First: '+top_five[0][0]+' ('+str(top_five[0][1])+') '\
                    +'Second: '+top_five[1][0]+' ('+str(top_five[1][1])+') '\
                    +'Third: '+top_five[2][0]+' ('+str(top_five[2][1])+') '\
                    +'Fourth: '+top_five[3][0]+' ('+str(top_five[3][1])+') '\
                    +'Fifth: '+top_five[4][0]+' ('+str(top_five[4][1])+')'

                        chat(irc, bot_says)
                    except:
                        bot_says = 'need more viewers to have a top 5.'
                        chat(irc, bot_says)

                elif message == '!points redeem':
                    bot_says = 'what to do with points. gamble?'\
                             + 'buy mod with 1M points? Kappa '

                    chat(irc, bot_says)

            sleep(1 / cfg.RATE)

def add_points(current_users):
    while True: 
        sleep(60)

        new_users = requests.get('https://tmi.twitch.tv/group/user/'\
                                 + cfg.CHAN[1:] + '/chatters')
        new_users = new_users.json()
        new_users = new_users['chatters']['moderators']\
                  + new_users['chatters']['viewers']

        if cfg.CHAN[1:] in current_users:
            streamer_online = True
            for user in current_users:
                if (user in new_users) and (user not in cfg.NO_POINTS):
                    with shelve.open(os.path.join(sys.path[0],cfg.CHAN[1:])) as s:
                        if user in s:
                            s[user] += 1
                        else:
                            s[user] = 1

            timestamped = False

            if cfg.CHAN[1:] not in new_users:
                logging.debug('streamer disconnected.')

        elif cfg.CHAN[1:] in new_users:
            streamer_online = True
            logging.debug('streamer online!')
            timestamped = False

        else: #streamer not in either user set (offline)
            streamer_online = False
            logging.debug('streamer offline.')

        if (not streamer_online) and (not timestamped):
            offline_time = datetime.now()
            timestamped = True
            logging.debug('offline_time set, '\
                    +'REDEEMED flagged for deletion.')

            between_streams = timedelta(hours=4)
            reset_claim = offline_time + between_streams

        if datetime.now() > reset_claim:
            try:
                os.remove(os.path.join(sys.path[0],cfg.CHAN[1:]\
                        +'REDEEMED.db'))
                logging.debug('file removed, users may redeem again.')
            except:
                logging.debug('  could not remove "redeemed, "'\
                        + 'file not found?')
            timestamped = False

        current_users = new_users


logging.basicConfig(filename=(os.path.join(sys.path[0], cfg.CHAN[1:]\
                            +'LOG.log')),level=logging.DEBUG)

irc = socket.socket()
irc.connect((cfg.HOST, cfg.PORT))

irc.send(bytes("PASS {}\r\n".format(cfg.PASS), 'utf-8'))
irc.send(bytes("NICK {}\r\n".format(cfg.NICK), 'utf-8'))
irc.send(bytes("JOIN {}\r\n".format(cfg.CHAN), 'utf-8'))

login_users = requests.get('https://tmi.twitch.tv/group/user/'\
                             + cfg.CHAN[1:] + '/chatters')
login_users = login_users.json()
login_users = login_users['chatters']['moderators']\
	      + login_users['chatters']['viewers']

logging.debug('Connected to '+cfg.CHAN[1:]+' with'+str(len(login_users))\
            +'users watching now.')

chat_loop = threading.Thread(name='chatbot', target=chatbot)
point_loop = threading.Thread(name='add_points', target=add_points,\
                              args=[login_users])


chat_loop.start()
point_loop.start()
