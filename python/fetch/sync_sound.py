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
from common import dateutil
import re
import os
import sys
import time
from urlparse import urlparse
reload(sys)
sys.setdefaultencoding('utf8')
fileOrige = "/home/file/sound"


def syncSound(itemId, url):
    parse = urlparse(url)
    outDir = fileOrige + os.path.dirname(parse.path)
    if os.path.exists(outDir) == False:
        os.makedirs(outDir)

    out = fileOrige + parse.path
    os.system("wget -O %s %s " % (out, url))


def parseLine(line=''):
    if len(line) > 0:
        lines = line.split(',')
        if len(lines) == 2:
            syncSound(int(lines[0]), lines[1])
        else:
            print 'error', line
if __name__ == '__main__':

    fh = open('../txt/sound.txt')
    for line in fh.readlines():
        parseLine(line.replace('\n', "").replace('\r', ''))
