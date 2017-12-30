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
from eroti import *
import re
import sys
import getopt
reload(sys)
sys.setdefaultencoding('utf8')
queue = MyQueue.MyQueue(200000)
maxCount = 1
parser = baseparse.BaseParse()

#艺术黄图#


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


def parseImg():
    obj = {}
    obj['name'] = "图片艺术"
    obj['baseurl'] = baseparse.baseurl
    obj['url'] = baseparse.baseurl
    obj['updateTime'] = datetime.datetime.now()
    queue.put(img.ImgParse(obj))
if __name__ == '__main__':

    for i in range(0, maxCount):
        worker = HandleThread("work-%s" % (i), queue)
        worker.start()
    parseImg()
