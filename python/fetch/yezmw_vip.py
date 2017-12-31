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
    objs = parser.fetchHeadChannel()
    print "video channel ok----项目=", len(objs)
    for obj in objs:
        videoPare = video.VideoParse(obj)
        videoPare.run()
if __name__ == '__main__':

    #     for i in range(0, maxCount):
    #         worker = HandleThread("work-%s" % (i), queue)
    #         worker.start()
    #     options, args = getopt.getopt(sys.argv[1:], "s:t:i:g")
    #     parseSound()
    parseVideo()
