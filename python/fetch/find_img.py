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
    print names
    return names

if __name__ == '__main__':

    imgIds = getImgs()
    names = listDir()
    error = []
    for imgId in imgIds:
        if names.count(str(imgId)) == 0:
            error.append(imgId)
            print imgId
    print error
