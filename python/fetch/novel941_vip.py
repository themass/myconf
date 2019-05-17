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
from novel941 import *
import re
import sys
import getopt
reload(sys)
sys.setdefaultencoding('utf8')

def parseText():
    textpo = text.TextChannelParse()
    textpo.run()
def parseText2():
    textpo = text2.TextChannelParse()
    textpo.run()
if __name__ == '__main__':
    parseText2()
