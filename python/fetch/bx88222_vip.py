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
from bx88222 import *
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
maxCount = 5
def parseText():
    textop = text.TextChannelParse()
    textop.run()
def parseImg():
    imgop = img.ImgParse()
    imgop.run()
if __name__ == '__main__':
    parseText()
    parseImg()