#!/usr/bin/env python3
# bot.py
#TODO: change print('statements') into logging.debug('statements')


import cfg

import logging
import shelve
import socket
import re
import requests
import threading
import os

from time import sleep
from datetime import datetime, timedelta


#regex, pulls chat from twitch irc 'response'.
chat_msg=re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

#regex, tries to extract an urbandictionary word's definition.
definition_regex = r'.definition.\:(.+?)(permalink.\:|author.\: ..|current_vot|thumbs_up.\:|thumbs_down|example.\:..|word.\:.....|defid.\:....)'


def chat(sock, msg):
    sock.send(bytes("PRIVMSG {} :{} \r\n".format(cfg.CHAN, msg), 'utf-8'))

def urban(word):
    built_url = 'https://api.urbandictionary.com/v0/define?term=' + word
    page = requests.get(built_url)
    page = str(page.json())
    
    if re.search(definition_regex, page):
        bot_says = re.search(definition_regex, page)
        bot_says = bot_says.group(0)
        bot_says = bot_says[15:-15]
        bot_says = word + '- ' + bot_says
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
        #print(username + ": " + message)


        if response == "PING :tmi.twitch.tv\r\n":
            irc.send(bytes("PONG :tmi.twitch.tv\r\n", 'utf-8'))

        else:
            if re.match(r'^!urban', message):

                bot_says = "i'm confused.. what did you ask?"

                print(username + ": " + message)

                if (message == '!urban') or (message == '!urban '):
                    bot_says = "!urban - defines a word using urban dictionary."

                #elif message == "!urban random":
                    #bot_says = 'TODO?'

                else:
                    search_term = message[7:]
                    bot_says = urban(search_term)

                chat(irc, bot_says)
                print('will.exe:', bot_says, '\n')

            elif re.match(r'^!will', message):

                bot_says = 'commands: !urban word - gives the urban ' \
                         + 'definition of a word (if it exists). '\
                         + '!points help - commands for !points. '\
                         + 'made with python.' 
                print(username + ": " + message)
                print('will.exe:', bot_says, '\n')

                chat(irc, bot_says)

            elif re.match(r'^!bots', message):

                bot_says = 'MrDestructoid'
                print(username + ": " + message)
                print('will.exe:', bot_says, '\n')
            
                chat(irc, bot_says)
            
            elif re.match(r'^!points', message):

                if (message == '!points') or (message == '!points '):
                    print(username + ": " + message)
                    with shelve.open(cfg.CHAN[1:]) as s:
                        if username in s:
                            user_points = str(s[username])
                            bot_says = '@' + username + ' has ' + user_points \
                                     + ' points.'
                        else:
                            bot_says = '@' + username + ' you got no points, '\
                                     + 'watch more stream bruh.'

                    print('will.exe:', bot_says + '\n')
                    chat(irc, bot_says)
                
                elif message == '!points help':
                    print(username + ": " + message)
                    bot_says = '@' + username + ' :' + '!points commands: ' \
                             + "'!points', '!points claim' " \
                             + "'!points top'. points cannot be earned while"\
                             + " streamer is offline."

                    print('will.exe:', bot_says + '\n')
                    chat(irc, bot_says)

                elif message == '!points claim':
                    print(username + ": " + message)
                    redeemed_filename = cfg.CHAN[1:] + 'REDEEMED'

                    current_users = requests.get(\
                                    'https://tmi.twitch.tv/group/user/'\
                                  + cfg.CHAN[1:] + '/chatters')
                    current_users = current_users.json()
                    current_users = current_users['chatters']['moderators']\
	                          + current_users['chatters']['viewers']

                    if cfg.CHAN[1:] in current_users:
                        with shelve.open(redeemed_filename) as redeemed:
                            if username in redeemed:
                                bot_says = '@'+username+' you may only claim '\
                                         + 'points once per stream.'
                            else:
                                with shelve.open(cfg.CHAN[1:]) as s:
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

                    print('will.exe:', bot_says + '\n')
                    chat(irc, bot_says)

                elif message == '!points top':
                    print(username + ": " + message)
                    try:
                        with shelve.open(cfg.CHAN[1:]) as s:
                            score_tups = sorted(s.items(), key=lambda x: \
                                                  x[1])[::-1]
                            top_five = score_tups[:5]

                            bot_says = '!points high scores: ' \
                    +'First: '+top_five[0][0]+' ('+str(top_five[0][1])+') '\
                    +'Second: '+top_five[1][0]+' ('+str(top_five[1][1])+') '\
                    +'Third: '+top_five[2][0]+' ('+str(top_five[2][1])+') '\
                    +'Fourth: '+top_five[3][0]+' ('+str(top_five[3][1])+') '\
                    +'Fifth: '+top_five[4][0]+' ('+str(top_five[4][1])+')'

                        print('will.exe:', bot_says + '\n')
                        chat(irc, bot_says)
                    except:
                        bot_says = 'idk LUL'
                        print('will.exe:', bot_says, '\n')
                        chat(irc, bot_says)

                elif message == '!points redeem':
                    print(username + ": " + message)
                    bot_says = 'what to do with points. gamble?'\
                             + 'buy mod with 1M points? Kappa '

                    print('will.exe:', bot_says + '\n')
                    chat(irc, bot_says)

            sleep(1 / cfg.RATE)

def add_points(current_users):
    while True: 
        sleep(60)
        print('checking users after 1 minute..')

        new_users = requests.get('https://tmi.twitch.tv/group/user/'\
                                 + cfg.CHAN[1:] + '/chatters')
        new_users = new_users.json()
        new_users = new_users['chatters']['moderators']\
                  + new_users['chatters']['viewers']

        if cfg.CHAN[1:] in current_users:
            streamer_online = True
            for user in current_users:
                if (user in new_users) and (user != cfg.CHAN[1:]):
                    if user not in cfg.NO_POINTS:
                        with shelve.open(cfg.CHAN[1:]) as s:
                            if user in s:
                                s[user] += 1
                            else:
                                s[user] = 1

            print('scores updated.\n')

            if cfg.CHAN[1:] not in new_users:
                print('streamer disconnected.\n')

        elif cfg.CHAN[1:] in new_users:
            streamer_online = True
            print('streamer online!\n')

        else: #streamer not in either user set (offline)
            streamer_online = False
            print('streamer offline.\n')

        if not streamer_online:

            offline_time = datetime.now()
            between_streams = timedelta(hours=4)
            reset_claim = offline_time + between_streams

            if datetime.now() > reset_claim:
                os.remove('./'+cfg.CHAN[1:]+'REDEEMED.db')
                print('file removed, users may redeem again.\n')

        current_users = new_users


irc = socket.socket()
irc.connect((cfg.HOST, cfg.PORT))

irc.send(bytes("PASS {}\r\n".format(cfg.PASS), 'utf-8'))
irc.send(bytes("NICK {}\r\n".format(cfg.NICK), 'utf-8'))
irc.send(bytes("JOIN {}\r\n".format(cfg.CHAN), 'utf-8'))

print('connected..\nlurkin tha server..')

current_users = requests.get('https://tmi.twitch.tv/group/user/'\
                             + cfg.CHAN[1:] + '/chatters')
current_users = current_users.json()
current_users = current_users['chatters']['moderators']\
	      + current_users['chatters']['viewers']

print(len(current_users), 'users watching now.\n')

chat_loop = threading.Thread(name='chatbot', target=chatbot)
point_loop = threading.Thread(name='add_points', target=add_points,\
                              args=[current_users])


chat_loop.start()
point_loop.start()
