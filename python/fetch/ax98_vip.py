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
from ax98 import *
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def parseVideo():
    videop = video.VideoParse()
    videop.run()
def parseVideo2():
    videop = video2.VideoParse()
    videop.run()
if __name__ == '__main__':
    parseVideo()
    parseVideo2()
