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
from se8 import *
import re
import sys
import getopt
reload(sys)
sys.setdefaultencoding('utf8')
baseurl = "https://www.ttt977.com"
reg = re.compile(r"(.*\/)\d+\.htm")
mp3Name = re.compile(r"<span>.*</span>")
queue = MyQueue.MyQueue(2000000)
maxCount = 4

parser = baseparse.BaseParse()

def parseText():
    lis = parser.fetchHead(u"情色小说")
    objs = parser.parsHeadText(lis)
    print "解析有情色小说 ok----项目=", len(objs)
    for obj in objs:
        handle = text.TextChannelParse(obj, queue)
        handle.run()
        print obj

if __name__ == '__main__':
    parseText()
    
