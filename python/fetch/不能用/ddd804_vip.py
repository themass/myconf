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
from fetch.ddd804 import *
import re
import sys
from fetch.ddd804 import *
reload(sys)
sys.setdefaultencoding('utf8')

def parseddd804Img():
    imgop = imgddd804.ImgParse()
    imgop.run()
def parsejiqingyazhouImg():
    imgop = imgjiqingyazhou.ImgParse()
    imgop.run()
def parse3wujiImg():
    imgop = img3wuji.ImgParse()
    imgop.run()
def parse58589sImg():
    imgop = img58589s.ImgParse()
    imgop.run()
def parse52cjgImg():
    imgop = img52cjg.ImgParse()
    imgop.run()
def parsejjj382Img():
    imgop = imgjjj382.ImgParse()
    imgop.run()
def parse65aeaeImg():
    imgop = img65aeae.ImgParse()
    imgop.run()
def parseasy1000Img():
    imgop = img65aeae.ImgParse()
    imgop.run()
def parseimgtlula44():
    imgop = imgtlula44.ImgParse()
    imgop.run()
def parseimgclickme():
    imgop = imgclickme.ImgParse()
    imgop.run()
def parseimggebi0():
    imgop = imggebi0.ImgParse()
    imgop.run()
def parsetextddd804():
    textpare = textddd804.TextChannelParse()
    textpare.run()
def parsetext65aeae(): 
    textpare = text65aeae.TextChannelParse()
    textpare.run()
def parseimgbx(): 
    imgop = imgbx.ImgParse()
    imgop.run()
def parsAll():
    parsejiqingyazhouImg()
    parse3wujiImg()
    parse58589sImg()
    parse52cjgImg()
    parsejjj382Img()
    parse65aeaeImg()
    parseasy1000Img()
    parseimgtlula44()
    parseddd804Img()
    parseimgclickme()
    parseimggebi0()
    parseimgbx()
if __name__ == '__main__':
    parseimgbx()
#     parse39vqImg()
# #      
#     parsedddImg()
#     parsejiqingyazhouImg()
