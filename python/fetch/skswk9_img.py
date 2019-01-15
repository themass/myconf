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
from skswk9 import *
import re
import sys
import getopt
reload(sys)
sys.setdefaultencoding('utf8')

def parseImg():
    for key, val in baseparse.img_channels.items():
        obj = {}
        obj['name'] = key
        obj['baseurl'] = baseparse.baseurl
        obj['url'] = val
        obj['updateTime'] = datetime.datetime.now()
        obj['channel'] = 'porn_sex'
#         queue.put(img.ImgParse(obj))
        handle = img.ImgParse(obj)
        handle.run()
def parseVideo():
    videop = video.VideoUserParse()
    videop.run()
def parseText():
    textpo = text.TextChannelParse()
    textpo.run()
if __name__ == '__main__':

    parseText()
#     parseImg()
#     parseVideo()
