#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author:End1ng

import pyinotify
import os,sys
import hashlib

class MyEventHandler(pyinotify.ProcessEvent):
    def process_IN_ACCESS(self, event):
        print "文件被访问:" + event.pathname.decode('utf-8')
    def process_IN_MODIFY(self, event):
        print "文件被写:" + event.pathname.decode('utf-8')
    def process_IN_ATTRIB(self, event):
        print "文件属性被修改:" + event.pathname.decode('utf-8')
    def process_IN_CLOSE_WRITE(self, event):
        print "可写文件被关闭:" + event.pathname.decode('utf-8')
    def process_IN_CLOSE_NOWRITE(self, event):
        print "不可写文件被关闭:" + event.pathname.decode('utf-8')
    def process_IN_OPEN(self, event):
        print "文件被打开:" + event.pathname.decode('utf-8')
    def process_IN_MOVED_FROM(self, event):
        print "文件被移走:" + event.pathname.decode('utf-8')
    def process_IN_MOVED_TO(self, event):
        print  "文件被移来:" + event.pathname.decode('utf-8')
    def process_IN_CREATE(self, event):
        print "创建新文件:" + event.pathname.decode('utf-8')
    def process_IN_DELETiE(self, event):
        print "文件被删除:" + event.pathname.decode('utf-8')
    def process_IN_DELETE_SELF(self, event):
        print "可执行文件删除:" + event.pathname.decode('utf-8')
    def process_IN_MOVE_SELF(self, event):
        print "可执行文件自移动:" + event.pathname.decode('utf-8')
    def process_IN_UNMOUNT(self, event):
        print "文件系统被umount:" + event.pathname.decode('utf-8')
    def process_IN_CLOSE(self, event):
        print "文件被关闭:" + event.pathname.decode('utf-8')
    def process_IN_MOVE(self, event):
        print "文件被移动:" + event.pathname.decode('utf-8')

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
        notok = False
        splittarget = os.path.basename(targetFile)
        for i in splittarget:
            # 如果文件名包含下面以外的字符 删除文件
            if i in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890._-":
                pass
            else:
                notok = True
        splittarget = splittarget.split(".")
        # 如果文件名含有一个以上的"."或者点后的字符不在白名单中，删除文件
        if splittarget.__len__() == 2 and splittarget[1] in whitelisting:
            pass
        else:
            notok = True
        if notok:
            os.remove(targetFile)
            print "[*]删除文件" + targetFile
        else:
            print "[*]允许新建" + targetFile

def removeStrInFile(targetFile):
     pass

def copyFiles(sourcepath,  destpath):
    global filehash
    for file in os.listdir(sourcepath):
        sourceFile = sourcepath + "/" + file
        targetFile = destpath + "/" + file
        if os.path.isfile(sourceFile):
            if not os.path.exists(destpath):
                os.makedirs(destpath)
            filecontent = open(sourceFile, "rb").read()
            md5file = hashlib.md5()
            md5file.update(filecontent)
            filehash[sourceFile.decode('utf-8')] = md5file.hexdigest()
            open(targetFile, "wb").write(filecontent)
        if os.path.isdir(sourceFile):
            copyFiles(sourceFile, targetFile)

def restoreFile(targetFile):
    try:
        filecontent = open(targetFile, "rb").read()
        md5file = hashlib.md5()
        md5file.update(filecontent)
        # 如果不比对hash，恢复文件时也会判为修改文件陷入死循环
        if filehash[targetFile] == md5file.hexdigest() :
            return
        print "文件被改动:" +  targetFile
        open(targetFile, "wb").write(open(backupdir + "/" + targetFile, "rb").read())
        print "[*]文件恢复成功" + targetFile
    except:
        pass



ARGS = MyArgparse()

# 备份地址
backupdir = ARGS['backupdir']

if not os.path.exists(backupdir):
    os.makedirs(backupdir)

if not os.path.exists(ARGS['logfile']):
    open(ARGS['logfile'], 'w')

# 初始化LOG
LOG = classlog(ARGS['logfile'],level=ARGS['debug'])
# 要监控目录 绝对路径
watchlist = ARGS['watchlist']
# 白名单列表
whitelisting = ARGS['ignore']

filehash = {}

for i in watchlist:
    if backupdir[-1] == "/":
        backupdir = backupdir[:-1]
    copyFiles(i,backupdir + i)

# watch manager
wm = pyinotify.WatchManager()
wm.add_watch(watchlist, pyinotify.ALL_EVENTS, rec=True)

# event handler
eh = MyEventHandler()

# notifier
notifier = pyinotify.Notifier(wm, eh)
notifier.loop()