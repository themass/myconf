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
from ni345 import *
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
def parseVideo():
    videop = video.VideoParse()
    videop.run()
# def parseText():
#     textop = text.TextChannelParse()
#     textop.run()
# def parseImg():
#     imgop = img.ImgParse()
#     imgop.run()
if __name__ == '__main__':
    parseVideo()