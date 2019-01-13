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
from kedouwo import *
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
def parseVideo4():
    videop = video4.VideoUserParse()
    videop.run()
def parseVideo5():
    videop = video5.VideoUserParse()
    videop.run()
def parseVideo6():
    videop = video6.VideoUserParse()
    videop.run()
def parseVideo7():
    videop = video7.VideoUserParse()
    videop.run()
def parseVideo8():
    videop = video8.VideoUserParse()
    videop.run()
def parseVideo9():
    videop = video9.VideoUserParse()
    videop.run()
def parseVideoALl():
    parseVideo()
    parseVideo2()
    parseVideo3()
    parseVideo4()
    parseVideo5()
    parseVideo6()
    parseVideo7()
    parseVideo8()
if __name__ == '__main__':
#     parseVideo()
#     parseVideo2()
#     parseVideo3()
    parseVideo4() 
#     parseVideo5()
#     parseVideo6()
#     parseVideo7()
#     parseVideo8()
