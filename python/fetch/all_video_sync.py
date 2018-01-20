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
import se8_vip
if __name__ == '__main__':

#webview
#     for channel, url in ozsese.baseparse.channels.items():
#         ozsesevideop = ozsese.video.VideoParse(channel, url)
#         ozsesevideop.run()
#     vj69videop = vj69.video.VideoParse()
#     vj69videop.run()
#     
#     
#     
#     
#    #翻墙 
#     
#     weavvideop = weav.video.VideoParse()
#     weavvideop.run()

    se8_vip.parseVideo()
#     singlovevideop = singlove.video.VideoParse()
#     singlovevideop.run()


