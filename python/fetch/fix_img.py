#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
import threading
from BeautifulSoup import BeautifulSoup
from common.envmod import *
from common import common
from common import typeutil
from common import db_ops
from common import MyQueue
from common import dateutil
from common import html_parse
import re
import os
import sys
import time
from urlparse import urlparse
reload(sys)
sys.setdefaultencoding('utf8')
queue = MyQueue.MyQueue(20000)
fileOrige = "/home/file/img_orige/"
fileCompress = "/home/file/img_compress/"
max_count = 10
idlist = []


def syncImgsObj():
    dbVPN = db.DbVPN()
    ops = db_ops.DbOps(dbVPN)
    objs = ops.getImgItems_itemUnSyncById(idlist)
    dbVPN.close()
    for obj in objs:
        ext = os.path.splitext(obj['picUrl'])[1]
        out = fileOrige + str(obj['id']) + ext
        os.system("wget -O %s %s " % (out, obj['picUrl']))
        os.system("mogrify  -resize 80%x80% " + out)
        print 'sync imgok url=', obj['picUrl']


def mv0K():
    os.system(
        "ll %s -h | awk -F' ' '{print$5" "$9}' | awk -F' ' '$1==0{print$2}'  | xargs -t -i mv {} /mnt/file/test/{}" % (fileOrige))


def getImgs():
    dbVPN = db.DbVPN()
    ops = db_ops.DbOps(dbVPN)
    items = ops.getImgItems_itemId()
    dbVPN.close()
    return items


def listDir():
    lists = os.listdir(fileOrige)
    names = []
    for item in lists:
        names.append(
            item.replace(".jpg", '').replace(".png", '').replace(".jpeg", ''))
    return names


def fix1():
    lists = os.listdir(fileOrige)
    for item in lists:
        out = fileOrige + item
        path = fileCompress + item
        count = 0
        if os.path.exists(path) == False:
            os.system("convert  -resize 50%x50% " + out + ' ' + path)
            print item, count, (count % 50)
            count += 1
            if (count % 50) == 0:
                print 'sleep'
                time.sleep(8)


def fix2():
    fh = open('fix_img.txt')
    for line in fh.readlines():
        count = 0
        if line.count("http") > 0:
            urls = line.splitlines(",")
            if len(urls) != 2:
                print 'error', line
                continue
            ext = os.path.splitext(urls[1])[1]
            out = fileOrige + str(urls[0]) + ext
            outjpg = fileOrige + str(urls[0]) + '.jpg'
            os.system("wget -O %s %s " % (out, urls[1]))
            os.system("mogrify  -resize 80%x80% " + out)
            if ext != 'jpg':
                os.system("convert  %s %s " % (out, outjpg))
            outComjpg = fileCompress + str(urls[0]) + '.jpg'
            commond = "convert  -resize 50%x50% " + outjpg + "  " + outComjpg
            print commond
            os.system(commond)
            count += 1
            if (count % 50) == 0:
                print 'sleep'
                time.sleep(8)
if __name__ == '__main__':
    #     mv0K()
    #     print 'mv ok'
    #     imgIds = getImgs()
    #     print 'imgIds ok'
    #     names = listDir()
    #     print 'listDir ok'
    #     for imgId in imgIds:
    #         if names.count(str(imgId)) == 0:
    #             idlist.append(imgId)
    #     print len(idlist), idlist
    #     syncImgsObj()
    fix1()
    fix2()
