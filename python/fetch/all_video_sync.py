#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
from common.envmod import *
import se8_vip
import yezmw_vip
import sp1769_vip
import ax98_vip
import kuyunzy_vip
import tianjiyy123_vip
import sp878_vip
import tzzy1399_vip
import kpd36_vip
import nfss_vip
import teshiw_vip
import sy88_vip
import nyg6_vip
from fetch import nvnvzx, nvnvzx_vip,  g6858_vip,\
    zooredtube_vip, qiezi_vip , dy1716_vip,\
     k9vidz_vip, kpd2_vip,\
    avzy88_vip, cmdy5_vip,xiangj_vip, av8_vip, xmhxmygs_vip, bx88222_vip,\
    nanguayingshi_vip, jinzidu_vip, ys88_vip, tv1009_vip, tlyy_vip

def pase1():
#     ax98_vip.parseVideo()
#     ax98_vip.parseVideo2()
    avzy88_vip.parseVideo()
    av8_vip.parseVideo()
    xmhxmygs_vip.parseVideo1()
    xmhxmygs_vip.parseVideo2()
def pase2():
    g6858_vip.parseVideo()
    kpd36_vip.parseVideo()
    jinzidu_vip.parseVideo()
    tv1009_vip.parseVideo()
def pase3():
    tianjiyy123_vip.parseVideo()
    kuyunzy_vip.parseVideo()
    kpd2_vip.parseVideo()
    ###ttyyy_vip.parseVideo()
def pase4():
    nyg6_vip.parseVideo()
    nyg6_vip.parseVideo2()

    nfss_vip.parseVideo2()
    nfss_vip.parseVideo3()
    nfss_vip.parseVideo4()
    nfss_vip.parseVideo5()
    k9vidz_vip.parseVideo()
def pase5():
    yezmw_vip.parseVideo()
    tzzy1399_vip.parseVideo()
def pase6():
    nvnvzx_vip.parseAll()
    k9vidz_vip.parseVideo()
    tlyy_vip.parseVideo()
    ###ppyy55_vip.parseUserVideo()
     
def pase7():
    qiezi_vip.parseVideo()
    xiangj_vip.parseVideo()
    se8_vip.parseVideo() 
    sp1769_vip.parseVideo()
    sp878_vip.parseVideo()
# 本机才能执行
def pase8():
    dy1716_vip.parseVideo()
    sy88_vip.parseVideo()
    cmdy5_vip.parseVideo()
    bx88222_vip.parseVideo()
    nanguayingshi_vip.parseVideo()
    ys88_vip.parseVideo()
def all():
#     pase1()
#     pase2()
#     pase3()
#     pase4()
#     pase5()
#     pase6()
#     pase7()
#     pase8()
    nvnvzx_vip.parseVideo7()
    se8_vip.parseVideo()
    se8_vip.parseSound()
if __name__ == '__main__':
#     pase8()
    val = argsMap.get("-p",0)
    if int(val)==1:
        pase1()
    elif int(val)==2:
        pase2()
    elif int(val)==3:
        pase3()
    elif int(val)==4:
        pase4()
    elif int(val)==5:
        pase5()
    elif int(val)==6:
        pase6()
    elif int(val)==7:
        pase7()
    elif int(val)==8:
        pase8()
    elif int(val)==10:
        all()
    else:
        print val,'error val',argsMap