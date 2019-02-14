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
import getopt
reload(sys)
sys.setdefaultencoding('utf8')
baseurl = "https://www.ttt977.com"
reg = re.compile(r"(.*\/)\d+\.htm")
mp3Name = re.compile(r"<span>.*</span>")
queue = MyQueue.MyQueue(2000000)
maxCount = 4

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
                obj = queue.get(block=True,timeout=2)
                if obj != None:
                    obj.run()
            except Exception as e:
                print common.format_exception(e)
                pass


def parseSound():
    print "解析有声小说 ok----项目="
    handle = sound.ChannelParse( queue)
    handle.run()
#         queue.put(sound.ChannelParse(obj, queue))


def parseText():
    lis = parser.fetchHead(u"情色小说")
    objs = parser.parsHeadText(lis)
    print "解析有情色小说 ok----项目=", len(objs)
    for obj in objs:
        handle = text.TextChannelParse(obj, queue)
        handle.run()
#         queue.put(text.TextChannelParse(obj, queue))
        print obj


def parseGirlImg():
    lis = parser.fetchHead(u"撸撸图区")
    print lis
    objs = parser.parsHeadText(lis)
    print "解析图片 ok----项目=", len(objs)
    for obj in objs:
        if obj.get("name") == "极品美女":
            handle = img_girl.ImgGrilParse(obj, queue)
            handle.run()
#             queue.put(img_girl.ImgGrilParse(obj, queue))
            print obj


def parseImg():
    lis = parser.fetchHead(u"激情图区")
    objs = parser.parsHeadText(lis)
    print "解析图片 ok----项目=", len(objs)
    for obj in objs:
        if obj.get("name") != "极品美女":
            handle = img.ImgParse(obj)
            handle.run()
#             queue.put(img.ImgParse(obj))
        print obj
def parseVideo():
    lis = parser.fetchHead(u"在线电影")
    objs = parser.parsHeadText(lis)
    print "解析在线视频 ok----项目=", len(objs)
    for obj in objs:
        handle = video.VideoParse(obj)
        handle.run()
#             queue.put(img.ImgParse(obj))
        print obj
def parseVideoRmb():
    lis = parser.fetchHead(u"手机下载")
    objs = parser.parsHeadText(lis)
    print "解析在线视频 ok----项目=", len(objs)
    for obj in objs:
        handle = video_rmb.VideoRmbParse(obj)
        handle.run()
#             queue.put(img.ImgParse(obj))
        print obj
def startWork():
    for i in range(0, maxCount):
        worker = HandleThread("work-%s" % (i), queue)
        worker.start()
if __name__ == '__main__':
    startWork()
    
    #     options, args = getopt.getopt(sys.argv[1:], "s:t:i:g")
#     parseSound()
    parseGirlImg()
    parseImg()
#     parseText()
#     parseVideo()
#     parseVideoRmb()
