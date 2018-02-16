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
from gif import *
import re
import sys
from fetch.gif import *
reload(sys)
sys.setdefaultencoding('utf8')

def parsewowantImg():
    imgop = imgwowant.ImgParse()
    imgop.run()
def parsehugao8Img():
    imgop = imghugao8.ImgParse()
    imgop.run()
def parseratooImg():
    imgop = imgratoo.ImgParse()
    imgop.run()
def parserneihanImg():
    imgop = imgneihanpa.ImgParse()
    imgop.run()
if __name__ == '__main__':
    parsewowantImg()
    parserneihanImg()
    parsehugao8Img()
    parseratooImg()
