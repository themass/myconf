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

channels1 = ['/htm/piclist3/', '/htm/piclist4/',
             '/htm/piclist2/', '/htm/piclist7/']
channels2 = ['/htm/tubaobao.htm', '/htm/piclist6/',
             '/htm/piclist8/', '/htm/piclist1/']

channels3 = ['/htm/girllist10/', '/htm/girllist16/', '/htm/girllist15/', '/htm/girllist8/',
             '/htm/girllist4/', '/htm/girllist3/', '/htm/girllist2/', '/htm/girllist1/']
channels4 = ['/htm/girllist7/', '/htm/girllist6/', '/htm/girllist5/',
             '/htm/girllist13/', '/htm/girllist14/', '/htm/girllist18/', '/htm/girllist17/']

imgUrl1 = 'http://img2.sspacee.com/file/img_orige/'
imgUrl2 = 'http://img3.sspacee.com/file/img_orige/'

imgcdnUrl1 = 'http://img2.cdn.sspacee.com/file/img_orige/'
imgcdnUrl2 = 'http://img3.cdn.sspacee.com/file/img_orige/'


class HandleThread(threading.Thread):

    def __init__(self, name, channels, imgUrl, imgCdnUrl):
        threading.Thread.__init__(self, name=name)
        self.t_name = name
        self.channels = channels
        self.imgUrl = imgUrl
        self.imgCdnUrl = imgCdnUrl

    def run(self):
        print self.channels
        for channel in self.channels:
            for i in range(4, 7):
                start = i * 100
                end = (i + 1) * 100
                items = self.getImgs(channel, start, end)
                if len(items) == 0:
                    break
                itemUrls = {}
                for obj in items:
                    try:
                        ext = os.path.splitext(obj['picUrl'])[1]
                        out = fileOrige + str(obj['id']) + ext
                        path = fileCompress + str(obj['id']) + ext
                        os.system("wget -O %s %s " % (out, obj['picUrl']))
                        os.system("mogrify  -resize 65%x65% " + out)
                        #os.system("convert  -resize 35%x35% " + out + ' ' + path)
                        print threading.current_thread().getName(), '----', str(obj['id']), '--url=', obj['picUrl']
                        itemUrls[obj['itemurl']] = 1
                    except Exception as e:
                        print obj['picUrl'], common.format_exception(e)
                self.updateImgUrl(itemUrls.keys())
            print '结束同步', channel

    def getImgs(self, channel, start, end):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        print threading.current_thread().getName(), '--page=', start
        items = ops.getImgItems_itemBySortType(sortType, channel, start, end)
        dbVPN.close()
        return items

    def updateImgUrl(self, itemUrl):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        ops.updateImgItemsFileUrl(itemUrl, self.imgCdnUrl, self.imgUrl)
        dbVPN.commit()
        dbVPN.close()
if __name__ == '__main__':
    for name, val in options:
        if name in ("-i"):
            if val == '1':
                print channels1, channels2
                worker1 = HandleThread(
                    "work-1", channels1, imgUrl1, imgcdnUrl1)
                worker1.start()
                worker2 = HandleThread(
                    "work-2", channels2, imgUrl1, imgcdnUrl1)
                worker2.start()
            elif val == '2':
                print channels3, channels4
                worker3 = HandleThread(
                    "work-1", channels3, imgUrl2, imgcdnUrl2)
                worker3.start()

                worker4 = HandleThread(
                    "work-2", channels4, imgUrl2, imgcdnUrl2)
                worker4.start()
            else:
                print 'i= 1 or 2'
