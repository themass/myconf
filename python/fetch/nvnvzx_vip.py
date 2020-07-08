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

def parseVideo3():
    videop = video3.VideoUserParse()
    videop.run()
def parseVideo5():
    videop = video5.VideoParse()
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
def parseAll():
    parseVideo3()
#     parseVideo5()
    parseVideo6()
    parseVideo7()
    parseVideo8()
if __name__ == '__main__':
    ###parseVideo()
#     parseAll()
#      parseVideo3()
# ##     #parseVideo4()
#     parseVideo8()
#     parseVideo6()
    parseVideo7()
