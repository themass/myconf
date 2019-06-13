# -*- coding: utf-8 -*-
from common import db_ops
from common import httputil
import os
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
reg = re.compile(
    r"rtt min/avg/max/mdev = ([0-9\.]+)/([0-9\.]+)/([0-9\.]+)")

domainList=['0spyr.8iwvsl.com',
'1.bp.blogspot.com',
'2.bp.blogspot.com',
'3.bp.blogspot.com',
'33img.com',
'4.bp.blogspot.com',
'4.share.photo.xuite.net',
'5b0988e595225.cdn.sohucs.com',
'86ar.8iwvsl.com',
'9844.8iwvsl.com',
'9tmz.8iwvsl.com',
'aimg.xyz',
'c.share.photo.xuite.net',
'cdn.clickme.net',
'cdn.pornpics.com',
'cdn1.snapgram.co',
'cdn2.snapgram.co',
'cdn3.snapgram.co',
'cdn4.snapgram.co',
'cdn5.snapgram.co',
'chuantupian.com',
'd2.xse2018.com',
'i.imgur.com',
'i1.buimg.com',
'image.wowant.com',
'imagetupian.nypd520.com',
'img.581gg.com',
'img.76rb.com',
'img.997pp.com',
'img.pic123456.com',
'img.xiatiantv.net',
'img5.showhaotu.xyz',
'img599.net',
'imghhh.secondary.space',
'imgs.isocialkey.com',
'is01.picsgonewild.com',
'ist3-6.filesor.com',
'jfkds.8iwvsl.com',
'mmslt1.com',
'mmtp1.com',
'nbvvv.8iwvsl.com',
'oi57.tinypic.com',
'oi58.tinypic.com',
'oi60.tinypic.com',
'opogx9ni8.bkt.clouddn.com',
'p.usxpic.com',
'p5.urlpic.club',
'p7.urlpic.club',
'pic.baidu.com.baidu-taobao-av.com',
'pic.bb164.com',
'pic.lookpic.xyz',
'pic.rmb.bdstatic.com',
'pic.sepapa.top',
'pic.xxappxx.xyz',
'pic.xxpicxx.xyz',
'pic.xxx55tp.com',
's1.1280inke.com',
's1.img26.com',
's1bfd.d39jcrlyy.com',
's1bfd.df34d3f.com',
's1kbfd.df34d3f.com',
's2.img26.com',
's2.xoimg.co',
's3.img26.com',
's5.img26.com',
's6.img26.com',
's7.img26.com',
's8.img26.com',
's9.img26.com',
'sbtv.8iwvsl.com',
'store4.imghost.eu',
'tu.ttt669.com',
'upics.ru',
'utya.8iwvsl.com',
'v1.kakade.info',
'ww1.sinaimg.cn',
'ww3.sinaimg.cn',
'ww4.sinaimg.cn',
'www.192tt.com',
'www.52cjg.com',
'www.52cjg.comhttp',
'www.58589s.com',
'www.chinatupic.com',
'www.eroti-cart.com',
'www.freecnmove.com',
'www.kpd129.com',
'www.lcylpic.com',
'www.mediafire.com',
'www.ratoo.net',
'www.singlove.com',
'www.touimg.com',
'www.ttbcdn.com',
'www.upimagesdowns.com',
'www.xiao88.top',
'www.xoimg.club',
'www1.wi.to',
'wx1.sinaimg.cn',
'wx2.sinaimg.cn',
'wx3.sinaimg.cn',
'wx4.sinaimg.cn',
'xxx.freeimage.us',]


def myAlign(string, length=0):
    if length == 0:
        return string
    slen = len(string)
    re = string
    if isinstance(string, str):
        placeholder = ' '
    else:
        placeholder = u'　'
    while slen < length:
        re += placeholder
        slen += 1
    return re


def parse(pingtexts):
    for line in pingtexts:
        if line.count("rtt min") > 0:
            match = reg.search(line)
            return match.group(2)
    return 10000

if __name__ == '__main__':
    errorList = []
    for item in domainList:
        cmd = 'ping  -c 2 -w 2 %s' % (item)
        lines = os.popen(cmd).readlines()
        print lines
        num = parse(lines)
        if num == 10000:
            print 'error ',item
    sys.exit()
