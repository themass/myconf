#!/usr/bin python
# -*- coding: utf-8 -*-
from common.envmod import *
import rqsxbyc_vip
import hsex_vip
import jiu667_vip
import xcvods_vip
import xx69_vip
import hanime_vip
import profile
import  ip38_vip
import tianlalu_vip
import hsck_vip
import md51_vip
import rqsxbyc_vip

if __name__ == '__main__':
    hsex_vip.parseVideo()
    hsck_vip.parseVideo()
    md51_vip.parseVideo()

    jiu667_vip.parseVideo()
    tianlalu_vip.parseVideo()
    xx69_vip.parseVideo(1, profile.maxVideoPage)
    xx69_vip.parseVideo2(1, profile.maxVideoPage)


    rqsxbyc_vip.parseVideo()
    xcvods_vip.parseVideo()
    hanime_vip.parseVideo()
    ip38_vip.parseVideo()

