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
import ir6y.video
import yezmw_vip
import xoxo164.video
import fff64_vip
import nomsgus_vip
import sexx77_vip
import sp1769_vip
import seman_vip
import zy3838_vip
import ttkyy_vip
import ax98_vip
import kuyunzy_vip
import tianjiyy123_vip
import urbanhenta_vip
import kump4_vip
import iir44_vip
import wuji3_vip
import zanquye_vip
import diediaody_vip
import tiantianyao_vip
import duotv_vip
import dadekai_vip
import upianku_vip
import meiyke_vip
import tt80_vip
import dxg11_vip
import mastv54_vip
import ggfuil_vip
import hanpian_vip
import miaobosp_vip
import pp56_vip
import ppyy55_vip
import sp878_vip
import tzzy1399_vip
import vj69_vip
import x2246_vip
import xoxo164_vip
import zxdy_vip
import zy3838_vip
import avhome11_vip
import s58589_vip
import hongxing_vip
import lusibi_vip
import s58589_vip
import qh_vip
import sifangpian_vip
import bt2n_vip
import xbshare_vip
import mayi01_vip
import ff326_vip
import fuli750_vip
import hs941_vip
import kpd36_vip
import cili_vip
import nfss_vip
import kedouwo_vip
import ava99_vip

def pase1():
    #webview
    for channel, url in ozsese.baseparse.channels.items():
        ozsesevideop = ozsese.video.VideoParse(channel, url)
        ozsesevideop.run()
    ####zy3838_vip.parseVideo()
    #####nomsgus_vip.parseVideo()
    lusibi_vip.parseVideo()
    hongxing_vip.parseVideo()
    ####avhome11_vip.parseVideo()
#     
    dxg11_vip.parseVideo()
    mastv54_vip.parseVideo()
    kedouwo_vip.parseVideo()
    kedouwo_vip.parseVideo2()
    kedouwo_vip.parseVideo3()
    kedouwo_vip.parseVideo4()
    kedouwo_vip.parseVideo5()
    kedouwo_vip.parseVideo6()
    kedouwo_vip.parseVideo7()
    nfss_vip.parseVideo()
    nfss_vip.parseVideo2()
    nfss_vip.parseVideo3()
    nfss_vip.parseVideo4()
def pase2():
    sexx77_vip.parseVideo()
    singlovevideop = singlove.video.VideoParse()
    singlovevideop.run()
  
    ####yezmw_vip.parseVideo()
    ####x2246_vip.parseVideo()
    ax98_vip.parseVideo()
  
    tianjiyy123_vip.parseVideo()
    #####tzzy1399_vip.parseVideo()
    
def pase3():
    seman_vip.parseVideo()
    kuyunzy_vip.parseVideo()
    kump4_vip.parseVideo()
    xbshare_vip.parseVideo()
    ttkyy_vip.parseVideo()
def pase4():
    zanquye_vip.parseVideo()
    diediaody_vip.parseVideo()
    #####dadekai_vip.parseVideo()
    upianku_vip.parseVideo()
    vj69_vip.paserVideo()
   
    
def pase5():
    meiyke_vip.parseVideo()
    sp878_vip.parseVideo()
    tiantianyao_vip.parseVideo()
###    xoxo164_vip.pareVideo()
    tzzy1399_vip.parseVideo()
    ####miaobosp_vip.parseVideo()
    ###速度较好
####    tt80_vip.parseVideo()
###    pp56_vip.parseVideo()
    ggfuil_vip.parseVideo()
    hanpian_vip.parseVideo()
    fuli750_vip.parseVideo()
    ####hs941_vip.parseVideo()
    kpd36_vip.parseVideo()
    cili_vip.parseVideo()
def pase6():
    se8_vip.parseVideo()
    ppyy55_vip.parseUserVideo()
    s58589_vip.parseVideo()
    qh_vip.parseVideo()
    sifangpian_vip.parseVideo()
    bt2n_vip.parseVideo()
    mayi01_vip.parseVideo()
    ff326_vip.parseVideo()
    ava99_vip.parseVideo()
    
def all():
    pase1()
    pase2()
    pase3()
    pase4()
    pase5()
    pase6()
if __name__ == '__main__':

    ####ir6yv = ir6y.video.VideoParse()
    ####ir6yv.run()
    ##urbanhenta_vip.parseVideo()
 ##    wuji3_vip.parseVideo()
###    duotv_vip.parseVideo()
##xoxo164videop = xoxo164.video.VideoParse()
##    xoxo164videop.run()
    ##iir44_vip.parseVideo()
###    fff64_vip.parseVideo()
####zxdy_vip.parseVideo()
###    sp1769_vip.parseVideo()
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
    elif int(val)==10:
        all()
    else:
        print val,'error val',argsMap