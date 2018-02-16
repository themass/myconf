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

def parseImg():
    obj = {}
    obj['name'] = "图片艺术"
    obj['baseurl'] = baseparse.baseurl
    obj['url'] = 'eroti-cart'
    obj['showType'] = 3
    obj['channel'] = 'hhh_sex'
    obj['updateTime'] = datetime.datetime.now()
    runner = img.ImgParse(obj)
    runner.run()
if __name__ == '__main__':

    parseImg()
