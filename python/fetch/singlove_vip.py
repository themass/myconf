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
from singlove import *
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
queue = MyQueue.MyQueue(200000)
maxCount = 2

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

def parseVideo():
    videop = video.VideoParse()
    videop.run()
def parseImg():
    obj = {}
    obj['name'] = 'H漫画-爽啊'
    obj['baseurl'] = baseparse.baseurl
    obj['channel'] = 'hhh_sex'
    obj['url'] = baseparse.imgChannelurl
    obj['updateTime'] = datetime.datetime.now()
    handle = img.ImgParse(obj)
    handle.run()
#     queue.put(img.ImgParse(obj))
if __name__ == '__main__':

    #     for i in range(0, maxCount):
    #         worker = HandleThread("work-%s" % (i), queue)
    #         worker.start()
    #     videop = video.VideoParse()
    #     videop.run()
    #     video.videoParse(queue)
#     parseImg()
