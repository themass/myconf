#!/usr/bin python
# -*- coding: utf-8 -*-
from nfss import *

import sys

reload(sys)
sys.setdefaultencoding('utf8')


def parseVideo2():
    videop = video2.VideoUserParse()
    videop.run()
def parseVideo3():
    videop = video3.VideoUserParse()
    videop.run()
def parseVideo4():
    videop = video4.VideoUserParse()
    videop.run()
def parseVideo5():
    videop = video5.VideoUserParse()
    videop.run()
if __name__ == '__main__':
#     parseVideo2()
    parseVideo4()
    #parseVideo3()
#     parseVideo5()
