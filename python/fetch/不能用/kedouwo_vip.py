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
from fetch.kedouwo import *
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def parseText12():
    textop = text12.TextChannelParse()
    textop.run()

if __name__ == '__main__':
#     parseVideo()
   # parseVideo14()
#     parseVideo3()
#     parseVideo4() 
#     parseVideo5()
#     parseVideo6()
#     parseVideo7()
#     parseVideo8()
#     parseVideo10()
#     parseVideo13()
    parseText12()
#     parseVideo15()