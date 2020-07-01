#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
from common.envmod import *
import se8_vip
import yezmw_vip
import fff64_vip
import sp1769_vip
import seman_vip
import ax98_vip
import kuyunzy_vip
import tianjiyy123_vip
import meiyke_vip
import dxg11_vip
import sp878_vip
import tzzy1399_vip
import bt2n_vip
import ff326_vip
import hs941_vip
import kpd36_vip
import cili_vip
import nfss_vip
import kedouwo_vip
import ava99_vip
import skswk9_img
import tlbfao_vip
import teshiw_vip
import newlynet_vip
import yin22_vip
import ttyyy_vip
import sy88_vip
import nyg6_vip
import s58589_vip
import ni345_vip
from fetch import nvnvzx, nvnvzx_vip,  g6858_vip,\
    zooredtube_vip, qiezi_vip, f2d_vip, xiangj_vip, siguo_vip, dy1716_vip,\
    japanbeast_vip, jinzidu_vip, k9vidz_vip, kpd2_vip, lele_vip, ozsese_vip,\
    singlove_vip, avzy88_vip, cmdy5_vip

def pase1():
    ax98_vip.parseVideo()
    ax98_vip.parseVideo2()
    avzy88_vip.parseVideo()
def pase2():
    g6858_vip.parseVideo()
    kpd36_vip.parseVideo()
def pase3():
    tianjiyy123_vip.parseVideo()
    tlbfao_vip.parseVideo()
    kuyunzy_vip.parseVideo()
    jinzidu_vip.parseVideo()
    kpd2_vip.parseVideo()
    ###ttyyy_vip.parseVideo()
def pase4():
    nyg6_vip.parseVideo()
    nyg6_vip.parseVideo2()

    nfss_vip.parseVideo2()
    nfss_vip.parseVideo4()
    k9vidz_vip.parseVideo()
def pase5():
    #kedouwo_vip.parseVideoAll()
    yezmw_vip.parseVideo()
    tzzy1399_vip.parseVideo()
def pase6():
    nvnvzx_vip.parseAll()
    k9vidz_vip.parseVideo()
    ###ppyy55_vip.parseUserVideo()
     
def pase7():
    ##qiezi_vip.parseVideo()
    xiangj_vip.parseVideo()
    se8_vip.parseVideo() 
    sp1769_vip.parseVideo()
    sp878_vip.parseVideo()
    zooredtube_vip.parseVideo()
# 本机才能执行
def pase8():
    dy1716_vip.parseVideo()
    sy88_vip.parseVideo()
    cmdy5_vip.parseVideo()

def all():
    pase1()
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