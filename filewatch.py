#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author:Ni7eip

import logging
import pyinotify
import os,sys
import hashlib
import argparse

class classlog(object):
    """log class"""
    def __init__(self,logfilename="log.txt",level="INFO"):
        level = level if level in ['CRITICAL','ERROR','WARNING','INFO','DEBUG','NOTSET'] else 'INFO'
        self.logger = logging.getLogger("classlog")
        self.logger.setLevel(logging.DEBUG)
        Fileformatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)-8s:%(message)s",
        datefmt='%Y-%m-%d %I:%M:%S %p')
        Streamformatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s:%(message)s",
        datefmt='%Y-%m-%d %I:%M:%S')# ,filename='example.log')

        Filelog = logging.FileHandler(logfilename)
        Filelog.setFormatter(Fileformatter)
        Filelog.setLevel(logging.DEBUG)

        Streamlog = logging.StreamHandler()
        Streamlog.setFormatter(Streamformatter)
        Streamlog.setLevel(level)

        self.logger.addHandler(Filelog)
        self.logger.addHandler(Streamlog)

    def debug(self,msg):
        self.logger.debug(msg)

    def info(self,msg):
        self.logger.info(msg)

    def warn(self,msg):
        self.logger.warn(msg)

    def error(self,msg):
        self.logger.error(msg)

    def critical(self,msg):
        self.logger.critical(msg)

class MyEventHandler(pyinotify.ProcessEvent):

    #IN_ACCESS，即文件被访问
    def process_IN_ACCESS(self, event):
        LOG.debug("文件被访问:" + event.pathname.decode('utf-8'))
    #IN_MODIFY，文件被write
    def process_IN_MODIFY(self, event):
        removeStrInFile(event.pathname.decode('utf-8'))
        restoreFile(event.pathname.decode('utf-8'))
    #IN_ATTRIB，文件属性被修改，如chmod、chown、touch等
    def process_IN_ATTRIB(self, event):
        LOG.debug("文件属性被修改:" + event.pathname.decode('utf-8'))
    #IN_CLOSE_WRITE，可写文件被close
    def process_IN_CLOSE_WRITE(self, event):
        LOG.debug("可写文件被关闭:" + event.pathname.decode('utf-8'))
    #IN_CLOSE_NOWRITE，不可写文件被close
    def process_IN_CLOSE_NOWRITE(self, event):
        LOG.debug("不可写文件被关闭:" + event.pathname.decode('utf-8'))
    #IN_OPEN，文件被open
    def process_IN_OPEN(self, event):
        LOG.debug("文件被打开:" + event.pathname.decode('utf-8'))
    #IN_MOVED_FROM，文件被移走,如mv
    def process_IN_MOVED_FROM(self, event):
        LOG.info("文件被移走:" + event.pathname.decode('utf-8'))
    #IN_MOVED_TO，文件被移来，如mv、cp
    def process_IN_MOVED_TO(self, event):
        # if event.pathname.decode('utf-8') in filehash:
            LOG.info( "文件被移来:" + event.pathname.decode('utf-8'))
            removeFileOrDir(event.pathname.decode('utf-8'))
    #IN_CREATE，创建新文件
    def process_IN_CREATE(self, event):
            LOG.info("创建新文件:" + event.pathname.decode('utf-8'))
            removeFileOrDir(event.pathname.decode('utf-8'))
    #IN_DELETE，文件被删除，如rm
    def process_IN_DELETiE(self, event):
        LOG.info("文件被删除:" + event.pathname.decode('utf-8'))
    #IN_DELETE_SELF，自删除，即一个可执行文件在执行时删除自己
    def process_IN_DELETE_SELF(self, event):
        LOG.info("可执行文件删除:" + event.pathname.decode('utf-8'))
    #IN_MOVE_SELF，自移动，即一个可执行文件在执行时移动自己
    def process_IN_MOVE_SELF(self, event):
        LOG.info("可执行文件移动:" + event.pathname.decode('utf-8'))
    #IN_UNMOUNT，宿主文件系统被umount
    def process_IN_UNMOUNT(self, event):
        LOG.info("文件系统被umount:" + event.pathname.decode('utf-8'))
    #IN_CLOSE，文件被关闭，等同于(IN_CLOSE_WRITE | IN_CLOSE_NOWRITE)
    def process_IN_CLOSE(self, event):
        LOG.debug("文件被关闭:" + event.pathname.decode('utf-8'))
    #IN_MOVE，文件被移动，等同于(IN_MOVED_FROM | IN_MOVED_TO)
    def process_IN_MOVE(self, event):
        LOG.info("文件被移动:" + event.pathname.decode('utf-8'))

def MyArgparse():
    parser = argparse.ArgumentParser(usage="%(prog)s [options]",add_help=False,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=(u'''
        作者：End1ng blog:end1ng.wordpress.com
        --------------------------------
            简单的一个文件监控脚本
            删除新增文件和文件夹
            恢复被修改的文件'''))
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('-h', '--help', action="store_true", help=u'显示当前帮助')
    optional.add_argument('--version', action='version', version='%(prog)s 1.0')

    args = parser.add_argument_group('Necessary arguments')
    args.add_argument('-w','--watchlist',metavar="目录",nargs='+',help="要监控的目录 多个用空格分隔")

    other = parser.add_argument_group('other arguments')
    other.add_argument('-b','--backupdir',metavar="目录",default="/tmp/filewatch/backup",help="备份的位置 默认/tmp/filewatch/backup")
    other.add_argument('--logfile',metavar="文件",default="/tmp/filewatch/filewatch.log",help="日志位置 默认/tmp/filewatch/filewatch.log")
    other.add_argument('--debug',action="store_true",help="输出详细的debug信息")
    args.add_argument('-i','--ignore',metavar="后缀",nargs='+',default=['jpg','png','gif'],help="允许的后缀,修改会覆盖。 默认jpg,png,gif")

    args=parser.parse_args()
    args = vars(args)
    if args['help'] or not args['watchlist']:
        parser.print_help()
        sys.exit()
    if args['debug']:
        args['debug'] = "DEBUG"

    return args

def removeFileOrDir(targetFile):
    if os.path.isdir(targetFile):
        fileslist = os.listdir(targetFile)
        for files in fileslist:
            removeFileOrDir(targetFile + "/" + files)
        try:
            os.rmdir(targetFile)
            LOG.info("[*]删除文件夹" + targetFile)
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
            LOG.info("[*]删除文件" + targetFile)
        else:
            LOG.info("[*]允许新建" + targetFile)

# def mkdirOrFile(file):
#     if not os.path.exists(os.path.dirname(file)):
#         os.makedirs(os.path.dirname(file))
#     if not os.path.exists(file):
#         open(file, 'w')

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
        LOG.info("文件被改动:" +  targetFile)
        open(targetFile, "wb").write(open(backupdir + "/" + targetFile, "rb").read())
        LOG.info("[*]文件恢复成功" + targetFile)
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