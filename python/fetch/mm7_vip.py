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
from mm7 import *
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def parseVideo(name):
    videop = video.VideoUserParse(name)
    videop.run()
if __name__ == '__main__':
#     parseVideo()
    val = argsMap.get("-p",0)
    if int(val)==1:
        parseVideo("header.html")
    elif int(val)==2:
        parseVideo("header2.html")
    elif int(val)==3:
        parseVideo("header3.html")
    elif int(val)==4:
        parseVideo("header4.html")
    elif int(val)==5:
        parseVideo("header5.html")