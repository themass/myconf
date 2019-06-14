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
from ff326 import *
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
def pareImg():
    imgrun = img.ImgParse()
    imgrun.run()
def parseText():
    textop = text.TextChannelParse()
    textop.run()
def parseVideo():
    videop = video.VideoUserParse()
    videop.run()
def parseVideo2():
    videop = video2.VideoUserParse()
    videop.run()
if __name__ == '__main__':
#     parseVideo()
    parseVideo2()
    pareImg()
    parseText()
