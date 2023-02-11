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
from fetch.xx69 import *
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def parseVideo(start,end):
    videop = video.VideoParse()
    videop.run(start,end)
if __name__ == '__main__':
    start = argsMap.get("-s",0)
    end = argsMap.get("-e",1)

    parseVideo(int(start), int(end))
