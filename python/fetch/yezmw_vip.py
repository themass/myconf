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
from yezmw import *
import re
import sys
import getopt
reload(sys)
sys.setdefaultencoding('utf8')

parser = baseparse.BaseParse()

def parseVideo():
    videoPare = video.VideoParse()
    videoPare.run()
if __name__ == '__main__':
    parseVideo()
