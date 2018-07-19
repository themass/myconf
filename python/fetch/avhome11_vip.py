#!/usr/bin python
# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup
from common.envmod import *
from avhome11 import *
reload(sys)
sys.setdefaultencoding('utf8')
def parseVideo():
    videop = video.VideoUserParse()
    videop.run()

def parseImg():
    imgop = img.ImgParse()
    imgop.run()
if __name__ == '__main__':
    parseVideo()
#     parseImg()
