# -*- coding: utf-8 -*-
# 自动增量备份插件（仅限Linux，在Ubuntu18.04通过测试）
# 定时运行：
# rsync -a --delete back-up/auto/ back-up/auto-last
# rsync -a --delete server/ back-up/auto
# author: Sciroccogti


import os
import platform
import re
import subprocess
import time
import yaml

from mcdreforged.api.all import *

PLUGIN_METADATA = {
    "id": "autobk",
    "version": "0.0.2",
    "name": "Auto backup with rsync on Linux",
    "author": "Sciroccogti",
    "link": "https://github.com/Dark-Night-Base/AutoBackup"
}

interval = 1  # hours between backups
path = ''
work_dir = ''
firsttime = False


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
    global path, work_dir, firsttime
    path = os.getcwd()  # MCDReforged/
    config = open(path + "/config.yml", "r")
    pluginconfig = yaml.load(config, Loader=yaml.CLoader)
    work_dir = pluginconfig['working_directory']
    try:
        os.listdir(path + '/back-up')
    except:
        server.logger.info(
            'Directory \'back-up\' not found, trying to create one...')
        os.mkdir(path + '/back-up')
    try:
        os.listdir(path + '/back-up/auto')
    except:
        server.logger.info(
            'Directory \'back-up/auto\' not found, trying to create one...')
        os.mkdir(path + '/back-up/auto')
        firsttime = True
    server.register_help_message(
        '!!autobk', 'Autoatically backup server files')


def on_info(server, info):
    global path, interval
    if re.match('!!autobk', info.content) != None:
        if info.is_player:
            if info.content == '!!autobk query':
                text = '§7Last backup is at\n'
                lasttime = get_FileAccessTime(path + '/back-up/auto')
                text += TimeStampToTime(lasttime)
                text += '\ninterval is %d hour' % interval
                server.tell(info.player, text)
            elif info.content.startswith('!!autobk set'):
                try:
                    new_interval = int(
                        re.match(r'!!autobk set (\S*)', info.content).groups()[0])
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
                text += '§7!!autobk query§r: Query the time of the last backup and the interval\n'
                text += '§7!!autobk set [hour]§r: Set the interval between backups, 0 to turn it off\n'
                server.tell(info.player, text)


def on_player_left(server, player):
    global firsttime, interval
    lasttime = get_FileAccessTime(path + '/back-up/auto')
    if firsttime or (interval > 0 and time.time() - lasttime >= 60 * 60 * interval):
        firsttime = False
        if platform.system() == 'Windows':
            text = '§cWindows is not supported by autobk yet!'
            server.say(text)
        else:
            try:
                err = subprocess.call(
                    ['rsync', '-a', '--delete', 'back-up/auto/', 'back-up/auto-last'])
            except Exception as err:
                text = '§cError during autobk:' + err
                server.say(text)
            else:
                try:
                    err = subprocess.call(
                        ['rsync', '-a', '--delete', work_dir + '/', 'back-up/auto'])
                except Exception as err:
                    text = '§cError during autobk:' + str(err)
                    server.say(text)
                else:
                    text = 'autobked successfully!'
                    server.logger.info(text)
                    server.say(text)
