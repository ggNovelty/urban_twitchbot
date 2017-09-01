#!/usr/bin/env python3
# bot.py


import cfg

import socket
import re
import requests
from time import sleep


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
    

chat_msg=re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
definition_regex = r'.definition.\:(.+?)(permalink.\:|author.\: ..|current_vot|thumbs_up.\:|thumbs_down|example.\:..|word.\:.....|defid.\:....)'


irc = socket.socket()
irc.connect((cfg.HOST, cfg.PORT))

irc.send(bytes("PASS {}\r\n".format(cfg.PASS), 'utf-8'))
irc.send(bytes("NICK {}\r\n".format(cfg.NICK), 'utf-8'))
irc.send(bytes("JOIN {}\r\n".format(cfg.CHAN), 'utf-8'))

print('connected..\nlurkin tha server..\n')

while True:
    response = irc.recv(1204).decode('utf-8')

    username = re.search(r"\w+", response).group(0)
    message = chat_msg.sub("", response)
    #print(username + ": " + message)


    if response == "PING :tmi.twitch.tv\r\n":
        irc.send(bytes("PONG :tmi.twitch.tv\r\n", 'utf-8'))


    else:
        if re.match(r'^!urban', message):

            bot_says = "i'm confused.. what did you ask?"
            message = message.rstrip()

            print(username + ": " + message)

            if (message == '!urban') or (message == '!urban '):
                bot_says = "!urban - defines a word using the urban dictionary."

            #elif message == "!urban random":
                #bot_says = 'TODO?'

            else:
                search_term = message[7:]
                bot_says = urban(search_term)

            chat(irc, bot_says)
            print('bot:', bot_says, '\n')

        elif re.match(r'^!bot', message):

            message = message.rstrip()

            bot_says = 'commands: !urban word - gives the urban ' \
                       + 'definition of a word (if it exists).' 
            print(username + ": " + message)
            print('bot:', bot_says, '\n')

            chat(irc, bot_says)

        elif re.match(r'^!bots', message):

            message = message.rstrip()

            bot_says = 'MrDestructoid'
            print(username + ": " + message)
            print('bot:', bot_says, '\n')
            
            chat(irc, bot_says)
            

        sleep(1 / cfg.RATE)
