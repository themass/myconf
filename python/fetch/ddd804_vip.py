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
from ddd804 import *
import re
import sys
from fetch.ddd804 import *
reload(sys)
sys.setdefaultencoding('utf8')

def parsedddImg():
    imgop = imgddd804.ImgParse()
    imgop.run()
def parsejiqingyazhouImg():
    imgop = imgjiqingyazhou.ImgParse()
    imgop.run()
def parse39vqImg():
    imgop = img39vq.ImgParse()
    imgop.run()
def parse3wujiImg():
    imgop = img3wuji.ImgParse()
    imgop.run()
if __name__ == '__main__':
    parse3wujiImg()
#     parse39vqImg()
#      
#     parsedddImg()
    parsejiqingyazhouImg()
