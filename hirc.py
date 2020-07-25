#!/usr/bin/python3
import os
import sys
import time
import threading
import random
import time
import json
from datetime import datetime
import irc_bot_noblock
import requests
import subprocess

# change it to your own
# get your oauth here: https://twitchapps.com/tmi/
# register app for client_id here https://glass.twitch.tv/console/apps/create
# make a unique name
# oauth redirect can be http://localhost (unless you have a redirect already)
# category is website integration

# the way this program pulls info if the channel is using the client_id
# giving access to some JSON info obtained through authorization

"""To run python hirc.py <channel name> <time between messages in minutes> <times to repeat (-1 is unlimited)>
   ON LINUX: To run in background add nohup before python and add & after times to repeat
   To end the process if running with -1 sys.argv use pgrep -a python
   then kill or pkill the process id"""

nickname = ''
oauth = ''
client_id = ''

is_live = ""

counter = int(0)

def ensure_dir(dir_path):
    if not os.path.exists(dir_path):
        print("creating directory " + dir_path)
        os.makedirs(dir_path)


def worker():
    global last_message
    while 1:
        last_message = input()
        time.sleep(0.01)


def safe_print(item):
    try:
        print(item)
    except Exception:
        print(item.encode('utf-8'))


def log_msg(name, msg):
    msg = msg.replace('\r', '').replace('\n', '')
    with open('./comment_log/' + chat_channel + ".txt", mode='a', encoding='utf-8') as log_file:
        log_file.write(datetime.utcnow().isoformat(sep='T') + "Z " + name + ': ' + msg + '\r\n')


def bot_messages():
    global counter
    with open("sayings.txt", "r") as ins:
        array = []
        for line in ins:
            array.append(line)
    value = random.choice(array)
    safe_print(">> " + nickname + ": " + value)
    bot.send_message(value)
    counter+=1
    timeTemp = time_mins*60
    
    if (cycles == -1):
        while (int(timeTemp) >= 600):
            timeTemp = helper_messages(timeTemp) 
            print('Time Left: ', timeTemp , '\n')
        time.sleep(timeTemp)
        get_status()
        
    if (counter == cycles):
        os.fork()
        os._exit(0)
        sys.exit("Kill Failed?")

    while (int(timeTemp) >= 600):
        timeTemp = helper_messages(timeTemp) 
        print('Time Left: ', timeTemp , '\n')
    
    time.sleep(timeTemp)


    

    #time.sleep(600)
    #time.sleep(600)
    #time.sleep(35) #35s
    #helper_messages()
    get_status()
    return

def helper_messages(timeTemp):
    #print("entered helper_messages():")
    helper = "/mods"
    safe_print(">> " + nickname + ": " + helper)
    bot.send_message(helper)
    log_msg(nickname, helper)
    time.sleep(600)
    return int(timeTemp)-600




def get_status():
    global is_live
    headers = {
        'Client-ID': client_id,
    }
    params = (
        ('user_login', chat_channel),
    )
    response = requests.get('https://api.twitch.tv/helix/streams', headers=headers, params=params)
    response
    data = json.loads(response.text)
    print("********************************************************")


    if len(data['data']) == 0:
        is_live = ""
    for elements in data['data']:
        is_live = elements['type']
        #print("For loop is live" + is_live)

    if (is_live != "live"):
        print("*                  Stream is offline.                  *")
        time.sleep(600)
        get_status()
    else:
        bot_messages()
        print("ONLINE!")
        get_status()


if(len(sys.argv) != 4): #originally !=2 arg1=hirc.py 2=channel 3=time between messages in minutes 4=total messages to be sent
    print (__file__ + ' chat_channel')
    print("python hirc.py <channel> <message timing> <messages to be sent (-1=unlimited)>")
    exit()
ensure_dir('./comment_log')
last_message = ''
chat_channel = sys.argv[1].lower().lstrip().rstrip()
chat_server = ['irc.chat.twitch.tv', 6667]
time_mins = int(sys.argv[2].lstrip().rstrip())
cycles = int(sys.argv[3].lstrip().rstrip())

bot = irc_bot_noblock.irc_bot(nickname, oauth, chat_channel, chat_server[0], chat_server[1])
bot.connect()
t = threading.Thread(target=worker)
t.start()



get_status()  # left over code



while 1:
    tmi_list = bot.get_parsed_message()  # get the message
    tmi_list.reverse()
    for item in [x for x in tmi_list if "." not in x.username]:
        message_orig = item.message.replace(chr(1) + "ACTION", "/me").replace(chr(1), '').lstrip().rstrip()
        log_msg(item.username, message_orig)
        safe_print(item.username + ": " + message_orig)

    if last_message != '':
        safe_print(">> " + nickname + ": " + last_message)
        bot.send_message(last_message)
        log_msg(nickname, last_message)
        last_message = ''
    time.sleep(0.01)
