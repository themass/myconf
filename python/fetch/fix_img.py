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
from urlparse import urlparse
reload(sys)
sys.setdefaultencoding('utf8')
queue = MyQueue.MyQueue(20000)
fileOrige = "/home/file/img_orige/"
fileCompress = "/home/file/img_compress/"
max_count = 10
idlist = []


def syncImgsObj(self):
    dbVPN = db.DbVPN()
    ops = db_ops.DbOps(dbVPN)
    objs = ops.getImgItems_itemUnSyncById(idlist)
    dbVPN.close()
    for obj in objs:
        ext = os.path.splitext(obj['picUrl'])[1]
        out = fileOrige + str(obj['id']) + ext
        os.system("wget -O %s %s " % (out, obj['picUrl']))
        os.system("mogrify  -resize 80%x80% %s" % (out))
        print 'sync imgok url=', obj['picUrl']


def mv0K():
    os.system(
        '''
        ll %s -h | awk -F' ' '{print$5"  "$9}' | awk -F' ' '$1==0{print$2}'  | xargs mv -t -i mv {} ../test/{}
        ''', fileOrige)


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
        names.append(item.replace(".jpg", ''))
    return names

if __name__ == '__main__':
    mv0K()
    imgIds = getImgs()
    names = listDir()
    for imgId in imgIds:
        if names.count(str(imgId)) == 0:
            idlist.append(imgId)
    print len(idlist), idlist
    syncImgsObj()
