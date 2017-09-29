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
max_count = 2

sortType = "2017-09-29"


class HandleThread(threading.Thread):

    def __init__(self, name, index):
        threading.Thread.__init__(self, name=name)
        self.t_name = name
        self.index = index

    def run(self):
        page = self.index
        index = 1
        while(True):
            items = self.getImgs(page)
            if len(items) == 0:
                print '结束同步', self.page
                break
            for obj in items:
                try:
                    ext = os.path.splitext(obj['picUrl'])[1]
                    out = fileOrige + str(obj['id']) + ext
                    path = fileCompress + str(obj['id']) + ext
                    os.system("wget -O %s %s " % (out, obj['picUrl']))
                    os.system("mogrify  -resize 30%x30% " + out)
                    os.system("convert  -resize 40%x40% " + out + ' ' + path)
                    print threading.current_thread().getName(), '----', str(obj['id']), '--url=', obj['picUrl']
                except Exception as e:
                    print obj['picUrl'], common.format_exception(e)
            time.sleep(10)
            page = index * max_count + self.index
            index = index + 1

    def getImgs(self, page):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        print threading.current_thread().getName(), '--page=', page
        items = ops.getImgItems_itemBySortType(sortType, page)
        dbVPN.close()
        return items

if __name__ == '__main__':

    for i in range(0, max_count):
        worker = HandleThread("work-%s" % (i), i)
        worker.start()
