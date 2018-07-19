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
from mayi01 import *
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def parseVideo():
    videop = video.VideoUserParse()
    videop.run()
def parseText():
    textpo = text.TextChannelParse()
    textpo.run()
def parseImg():
    imgop = img.ImgParse()
    imgop.run()
if __name__ == '__main__':
#     parseText()
    parseVideo()
#     parseImg()
