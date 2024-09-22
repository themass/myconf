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
from fetch.noval1024 import *
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def parseText():
    textP = textyi2212.TextChannelParse()
    textP.run()
def parseText2():
    textP = text1006ty.TextChannelParse()
    textP.run()
def parseText4():
    textP = textyazhouse8.TextChannelParse()
    textP.run()
def parseText5():
    textP = textbook18.TextChannelParse()
    textP.run()
if __name__ == '__main__':
    parseText5()
    # parseText4()
    # parseText2()
    # parseText()
