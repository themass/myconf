#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
from fetch.porn91 import *
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def parseVideo():
    videop = video.VideoParse()
    videop.run()
def parseText():
    textP = text.TextChannelParse()
    textP.run()
if __name__ == '__main__':
    parseText()
