# -*- coding: utf-8 -*-

import time
import os
import re
import platform
import subprocess
from utils import config, constant

interval = 1  # hours between backups
path = ''
work_dir = ''

def TimeStampToTime(timestamp: float) -> str:
    "convert timestamp to time (str)"
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)


def get_FileAccessTime(filePath: str) -> float:
    "get the last accessed time in timestamp (sec)"
    # filePath = unicode(filePath, 'utf8')
    try:
        t = os.path.getatime(filePath)
    except:
        t = -1
    return t


def on_load(server, old_module):
    global path
    global work_dir
    pluginconfig = config.Config(constant.CONFIG_FILE)
    pluginconfig.read_config()
    work_dir = pluginconfig['working_directory']
    path = os.getcwd()  # MCDReforged/
    try:
        os.listdir(path + '/back-up')
    except:
        server.say('§eDirectory \'back-up\' not found, trying to create one...')
        server.logger.info(
            'Directory \'back-up\' not found, trying to create one...')
        os.mkdir(path + '/back-up')
        os.listdir(path + '/back-up')


def on_info(server, info):
    global path
    global interval
    if re.match('!!autobk', info.content) != None:
        if info.is_player:
            if info.content == '!!autobk query':
                text = 'Last backup is at'
                lasttime = get_FileAccessTime(path + '/back-up/auto')
                text += TimeStampToTime(lasttime)
                server.tell(info.player, text)
            elif info.content.startswith('!!autobk set'):
                try:
                    new_interval = int(
                        re.match('!!autobk set (\S*)', info.content).groups()[0])
                except:
                    text = '§cPlease enter an interger!'
                    server.tell(info.player, text)
                else:
                    interval = new_interval
                    if interval == 0:
                        text = 'autobk is turned OFF'
                        server.say(text)
                    else:
                        text = 'autobk interval is set to %d' % interval
                        server.say(text)
            else:
                text = '§7!!autobk§r: Show this message\n'
                text += '§7!!autobk set [hour]§r: Set the interval between backups, 0 to turn it off\n'
                text += '§7!!autobk query§r: Query the time of the last backup and the interval'
                server.tell(info.player, text)


def on_player_left(server, player):
    lasttime = get_FileAccessTime(path + '/back-up/auto')
    if time.time() - lasttime >= 60 * 60 * interval:
        if platform.system() == 'Windows':
            text = '§cWindows is not supported by autobk yet!'
            server.say(text)
        else:
            try:
                err = subprocess.call(['rsync', '-a', '--delete', 'back-up/auto/', 'back-up/auto-last'])
            except:
                text = '§cError during autobk:' + err
                server.say(text)
            else:
                try:
                    err = subprocess.call(['rsync', '-a', '--delete', work_dir, 'back-up/auto'])
                except Exception as err:
                    text = '§cError during autobk:' + str(err)
                    server.say(text)
                else:
                    text = 'autobk successfully!'
                    server.say(text)
