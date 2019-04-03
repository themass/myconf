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

def parseText12():
    textop = text12.TextChannelParse()
    textop.run()
    
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
def parseVideo10():
    videop = video10.VideoUserParse()
    videop.run()
def parseVideo9():
    videop = video9.VideoUserParse()
    videop.run()
def parseVideo11():
    videop = video11.VideoParse()
    videop.run()
def parseVideo12():
    videop = video12.VideoUserParse()
    videop.run()
def parseVideo13():
    videop = video13.VideoUserParse()
    videop.run()
def parseVideo14():
    videop = video14.VideoUserParse()
    videop.run()
def parseVideoALl():
    #####parseVideo9()
#     parseVideo2()
    parseVideo3() 
    parseVideo4()
    parseVideo5()
    parseVideo6()
    parseVideo7()
    parseVideo8()
    parseVideo10()
    parseVideo11()
    parseVideo12()
    parseVideo13()
    parseVideo14()
if __name__ == '__main__':
#     parseVideo()
#     parseVideo14()
    parseVideo3()
#     parseVideo4() 
#     parseVideo5()
#     parseVideo6()
#     parseVideo7()
#     parseVideo8()
#     parseVideo10()
#     parseVideo13()
#     parseVideo8()
