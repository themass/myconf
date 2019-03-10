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
from nvnvzx import *
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def parseVideo():
    videop = video.VideoUserParse()
    videop.run()
def parseVideo2():
    videop = video2.VideoUserParse()
    videop.run()
def parseVideo3():
    videop = video3.VideoUserParse()
    videop.run()
def parseVideo5():
    videop = video5.VideoParse()
    videop.run()
def parseVideo6():
    videop = video6.VideoUserParse()
    videop.run()
def parseAll():
#     parseVideo()
#     parseVideo2()
    parseVideo3()
    parseVideo5()
    parseVideo6()
if __name__ == '__main__':
    ###parseVideo()
    parseAll()
#      parseVideo3()
# ##     #parseVideo4()
#      parseVideo5()
#     parseVideo6()
#     parseVideo7()
