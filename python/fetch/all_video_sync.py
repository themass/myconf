#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
from common.envmod import *
import vj69.video
import ozsese.video
import ozsese.baseparse
import singlove.video
import weav.video
if __name__ == '__main__':

    for channel, url in ozsese.baseparse.channels.items():
        ozsesevideop = ozsese.video.VideoParse(channel, url)
        ozsesevideop.run()
    vj69videop = vj69.video.VideoParse()
    vj69videop.run()
    
    weavvideop = weav.video.VideoParse()
    weavvideop.run()


#     singlovevideop = singlove.video.VideoParse()
#     singlovevideop.run()


