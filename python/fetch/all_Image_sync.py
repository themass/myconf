#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
from common.envmod import *
#艺术图片，需要下载到德国及
import eroti_img
#美图
import tt192_vip
#黄土
import fhn_vip
#黄土
import se8_vip
#漫画
import singlove_vip
#黄土
import skswk9_img


if __name__ == '__main__':
    eroti_img.parseImg()
    fhn_vip.parseImg()
    se8_vip.startWork()
    se8_vip.parseGirlImg()
    se8_vip.parseImg()
    singlove_vip.parseImg()
    skswk9_img.parseImg()
    
#     tt192_vip.parseImg()

#     for channel, url in ozsese.baseparse.channels.items():
#         ozsesevideop = ozsese.video.VideoParse(channel, url)
#         ozsesevideop.run()
#     vj69videop = vj69.video.VideoParse()
#     vj69videop.run()

#     singlovevideop = singlove.video.VideoParse()
#     singlovevideop.run()


