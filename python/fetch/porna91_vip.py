#!/usr/bin python
# -*- coding: utf-8 -*-
from fetch.porna91 import *
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def parseText():
    textP = text.TextChannelParse()
    textP.run()


def parseVideo():
    videop = video.VideoParse()
    videop.run()


if __name__ == '__main__':
    parseText()
