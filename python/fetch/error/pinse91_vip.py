#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
from fetch.pinse91 import *
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def parseVideo():
    videop = video.VideoParse()
    videop.run()
if __name__ == '__main__':
    parseVideo()
