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
from se8 import *
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
baseurl = "https://www.eee991.com"
reg = re.compile(r"(.*\/)\d+\.htm")
mp3Name = re.compile(r"<span>.*</span>")
queue = MyQueue.MyQueue(200000)
maxCount = 5

parser = baseparse.BaseParse()


class HandleThread(threading.Thread):

    def __init__(self, name, queue):
        threading.Thread.__init__(self, name=name)
        self.t_name = name
        self.t_queue = queue

    def run(self):
        while(True):
            try:
                print queue.qsize()
                obj = queue.get(timeout=30)
                if obj != None:
                    obj.run()
            except Exception as e:
                print common.format_exception(e)
                pass


def parseSound():
    lis = parser.fetchHead(u"有声小说")
    objs = parser.parsHeadText(lis)
    print "解析有声小说 ok----项目=", len(objs)
    for obj in objs:
        queue.put(sound.ChannelParse(obj, queue))


def parseText():
    lis = parser.fetchHead(u"情色小说")
    objs = parser.parsHeadText(lis)
    print "解析有情色小说 ok----项目=", len(objs)
    for obj in objs:
        queue.put(text.TextChannelParse(obj, queue))
        print obj


def parseGirlImg():
    lis = parser.fetchHead(u"图区")
    objs = parser.parsHeadText(lis)
    print "解析图片 ok----项目=", len(objs)
    for obj in objs:
        if obj.get("name") == "极品美女":
            queue.put(img_girl.ImgGrilParse(obj, queue))
            print obj


def parseImg():
    lis = parser.fetchHead(u"图区")
    objs = parser.parsHeadText(lis)
    print "解析图片 ok----项目=", len(objs)
    for obj in objs:
        queue.put(img.ImgParse(obj))
        print obj
if __name__ == '__main__':

    for i in range(0, maxCount):
        worker = HandleThread("work-%s" % (i), queue)
        worker.start()
#     parseSound()
#     parseGirlImg()
    parseImg()
    parseText()
