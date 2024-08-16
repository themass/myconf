#!/usr/bin python
# -*- coding: utf-8 -*-
from fetch.missav import *
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def parseVideo():
    videop = video.VideoParse()
    videop.run()
def parseVideo2():
    videop = video2.VideoUserParse()
    videop.run()
if __name__ == '__main__':

    # parseVideo()
    parseVideo2()
