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
from fff64 import *
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
queue = MyQueue.MyQueue(200000)
maxCount = 5

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

#     queue.put(img.ImgParse(obj))
def parseVideo():
    videop = video.VideoParse()
    videop.run()
def parseText():
    textop = text.TextChannelParse()
    textop.run()
def parseImg():
    imgop = img.ImgParse()
    imgop.run()
if __name__ == '__main__':
    parseVideo()
    parseText()
    parseImg()