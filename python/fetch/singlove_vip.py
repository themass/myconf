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
if __name__ == '__main__':

    #     videop = video.VideoParse()
    #     videop.run()
    #     video.videoParse(queue)
    parseImg()
