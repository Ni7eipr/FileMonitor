#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 文件监控轻量版

import pyinotify
import os,sys
import hashlib

class MyEventHandler(pyinotify.ProcessEvent):
    def process_IN_OPEN(self, event):
        output("打开文件:" + event.pathname) if debug else 0
        open(logfile, 'a').write("打开文件:" + event.pathname + "\n")
    def process_IN_CREATE(self, event):
        print "创建文件:" + event.pathname
        open(logfile, 'a').write("创建文件:" + event.pathname + "\n")
        0 if Onlywatch else removeFileOrDir(event.pathname)
    def process_IN_MOVED_TO(self, event):
        print  "文件移入:" + event.pathname
        open(logfile, 'a').write("文件移入:" + event.pathname + "\n")
        0 if Onlywatch else removeFileOrDir(event.pathname)
    def process_IN_MODIFY(self, event):
        print "文件改动:" + event.pathname
        open(logfile, 'a').write("文件改动:" + event.pathname + "\n")
        0 if Onlywatch else restoreFile(event.pathname)

def output(data):
    print data

def getMd5(data):
    md5file = hashlib.md5()
    md5file.update(data)
    return md5file.hexdigest()

def copyFiles(sourcepath,  destpath):
    global filehash
    for file in os.listdir(sourcepath):
        sourceFile = sourcepath + '/' + file
        targetFile = destpath + '/' + file

        if os.path.isfile(sourceFile):
            if not os.path.exists(destpath):
                os.makedirs(destpath)

            filecontent = open(sourceFile, 'rb').read()
            filehash[sourceFile] = getMd5(filecontent)

            open(targetFile, 'wb').write(filecontent)

        if os.path.isdir(sourceFile):
            copyFiles(sourceFile, targetFile)

def removeFileOrDir(targetFile):
    if os.path.isdir(targetFile):
        fileslist = os.listdir(targetFile)
        for files in fileslist:
            removeFileOrDir(targetFile + "/" + files)
        try:
            os.rmdir(targetFile)
            print "[*]删除文件夹" + targetFile
        except:
            pass

    if os.path.isfile(targetFile):
        ext = os.path.splitext(targetFile)[-1]
        if 'ph' in ext:
            print "[*]删除文件" + targetFile
        else:
            print "[*]允许新建" + targetFile

def restoreFile(targetFile):
    try:
        filecontent = open(targetFile, 'rb').read()
        # 如果不比对hash，恢复文件时也会判为修改文件陷入死循环
        if filehash[targetFile] == getMd5(filecontent):
            return
        open(targetFile, 'wb').write(open(backupdir + '/' + targetFile, 'rb').read())
        print '[*]文件恢复成功' + targetFile
    except:
        pass

if sys.argv.__len__() > 1 and os.path.exists(sys.argv[1]):
    watchlist = sys.argv[1]
else:
    sys.exit('useage:\n\tpython fileWatchList 目录\n\t-w 仅监控\n\t-d 开启debug')

debug = True if '-d' in sys.argv else False
Onlywatch = True if '-w' in sys.argv else False
bakdir = '/tmp/filewatch/'
backup = bakdir + 'backup/'
logfile = bakdir + 'log.txt'
filehash = {}

copyFiles(watchlist,backup + watchlist) if '-w' not in sys.argv else 0

# watch manager
wm = pyinotify.WatchManager()
wm.add_watch(watchlist, pyinotify.ALL_EVENTS, rec=True)

# event handler
eh = MyEventHandler()

# notifier
notifier = pyinotify.Notifier(wm, eh)
notifier.loop()