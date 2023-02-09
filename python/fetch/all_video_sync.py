#!/usr/bin python
# -*- coding: utf-8 -*-
from common.envmod import *
import se8_vip
import kuyunzy_vip
import nfss_vip
from fetch.不能用 import nanguayingshi_vip, g6858_vip, duorydonng_vip, nyg6_vip, k9vidz_vip, cmdy5_vip, sp878_vip, \
    kpd36_vip, qiezi_vip, avzy88_vip, sy88_vip, kpd2_vip, nvnvzx_vip, sp1769_vip, jinzidu_vip, ys88_vip, tzzy1399_vip, \
    tianjiyy123_vip, bx88222_vip, yezmw_vip


def pase1():
#     ax98_vip.parseVideo()
#     ax98_vip.parseVideo2()
    avzy88_vip.parseVideo()
def pase2():
    g6858_vip.parseVideo()
    kpd36_vip.parseVideo()
    jinzidu_vip.parseVideo()
def pase3():
    tianjiyy123_vip.parseVideo()
    kuyunzy_vip.parseVideo()
    kpd2_vip.parseVideo()
    duorydonng_vip.parseVideo()
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
    ###ppyy55_vip.parseUserVideo()
     
def pase7():
    qiezi_vip.parseVideo()
    se8_vip.parseVideo() 
    sp1769_vip.parseVideo()
    sp878_vip.parseVideo()
# 本机才能执行
def pase8():
    sy88_vip.parseVideo()
    cmdy5_vip.parseVideo()
    bx88222_vip.parseVideo()
    nanguayingshi_vip.parseVideo()
    ys88_vip.parseVideo()
def all():
    #pase1()
    pase2()
    pase3()
    pase4()
    pase5()
    pase6()
    pase7()
    pase8()
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