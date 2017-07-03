#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 文件监控轻量版

import pyinotify
import os,sys
import hashlib
import signal

if sys.argv.__len__() > 1 and os.path.exists(sys.argv[1]) and sys.argv[1][0] == '/':
    watchlist = sys.argv[1]
else:
    sys.exit('useage:\n\tpython fileWatchList /var/www/html\n\t-w 仅监控\n\t-d 开启debug')

debug = True if '-d' in sys.argv else False
onlywatch = True if '-w' in sys.argv else False
bakdir = '/tmp/filewatch/'
backup = bakdir + 'backup'
logfile = bakdir + 'log.txt'

file_hash = {}
class MyEventHandler(pyinotify.ProcessEvent):
    def process_IN_OPEN(self, event):
        output("打开文件:" + event.pathname)
    def process_IN_CREATE(self, event):
        output("创建文件:" + event.pathname, 1)
        if not onlywatch:
            if 'ph' not in os.path.splitext(event.pathname)[-1] or event.pathname in file_hash:
                output("[*]创建文件:" + event.pathname, 1)
            else:
                removeFileOrDir(event.pathname)
    def process_IN_MOVED_TO(self, event):
        output("移入文件:" + event.pathname, 1)
        if not onlywatch:
            if 'ph' in os.path.splitext(event.pathname)[-1]:
                removeFileOrDir(event.pathname)
            else:
                output("[*]移入文件:" + event.pathname, 1)
    def process_IN_MODIFY(self, event):
        output("改动文件:" + event.pathname, 1)
        if not onlywatch:
            if event.pathname in file_hash:
                if file_hash[event.pathname] == getMd5(open(event.pathname, 'rb').read()):
                    output("[*]文件无变化:" + event.pathname, 1)
                else:
                    restoreFile(event.pathname)
                    output("[*]恢复文件:" + event.pathname, 1)
            else:
                output("[*]改动文件:" + event.pathname, 1)
    def process_IN_DELETE(self, event):
        output("删除文件:" + event.pathname, 1)
        if not onlywatch:
            if event.pathname in file_hash:
                output("[*]删除文件:" + event.pathname, 1)
                restoreFile(event.pathname)
                output("[*]恢复文件:" + event.pathname, 1)
            else:
                output("[*]删除文件:" + event.pathname, 1)

def output(text, debug=debug):
    open(logfile, 'a').write(text + "\n")
    if debug:
        print text

def getMd5(data):
    md5file = hashlib.md5()
    md5file.update(data)
    return md5file.hexdigest()

def copyFiles(sourcepath,  destpath):
    global file_hash
    for file in os.listdir(sourcepath):
        sourceFile = sourcepath + '/' + file
        targetFile = destpath + '/' + file
        if os.path.isfile(sourceFile):
            if not os.path.exists(destpath):
                os.makedirs(destpath)
            filecontent = open(sourceFile, 'rb').read()
            open(targetFile, 'wb').write(filecontent)
            if 'ph' in os.path.splitext(sourceFile)[-1]:
                file_hash[sourceFile] = getMd5(filecontent)
        if os.path.isdir(sourceFile):
            copyFiles(sourceFile, targetFile)

def removeFileOrDir(targetFile):
    if os.path.isdir(targetFile):
        fileslist = os.listdir(targetFile)
        for files in fileslist:
            removeFileOrDir(targetFile + "/" + files)
        try:
            os.rmdir(targetFile)
        except:
            pass

    if os.path.isfile(targetFile):
        os.remove(targetFile)

def restoreFile(targetFile):
    open(targetFile, 'wb').write(open(backup + targetFile, 'rb').read())

def CtrlCHandler(signum, frame):
    sys.exit("\n再见")

signal.signal(signal.SIGINT, CtrlCHandler)

try:
    copyFiles(watchlist,backup + watchlist) if '-w' not in sys.argv else 0
except (IOError, OSError),e:
    print e

# watch manager
wm = pyinotify.WatchManager()
wm.add_watch(watchlist, pyinotify.ALL_EVENTS, rec=True)

# event handler
eh = MyEventHandler()

# notifier
notifier = pyinotify.Notifier(wm, eh)
notifier.loop()