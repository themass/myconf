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

domainList=['img.581gg.com',
'www.singlove.com',
'imghhh.secondary.space',
'img.997pp.com',
'www.upimagesdowns.com',
'img5.showhaotu.xyz',
'chuantupian.com',
'9tmz.8iwvsl.com',
'sbtv.8iwvsl.com',
'0spyr.8iwvsl.com',
'86ar.8iwvsl.com',
'9844.8iwvsl.com',
'jfkds.8iwvsl.com',
'utya.8iwvsl.com',
's1bfd.d39jcrlyy.com',
'wx2.sinaimg.cn',
'wx3.sinaimg.cn',
'wx4.sinaimg.cn',
'wx1.sinaimg.cn',
'tu.ttt669.com',
'www.58589s.com',
'p7.urlpic.club',
'p5.urlpic.club',
'p.usxpic.com',
'www.touimg.com',
'pic.baidu.com.baidu-taobao-av.com',
'pic.xxpicxx.xyz',
'pic.lookpic.xyz',
'www.chinatupic.com',
'mmtp1.com',
'www.192tt.com',
'xxx.freeimage.us',
'33img.com',
's1.1280inke.com',
'i1.buimg.com',
's1.img26.com',
's9.img26.com',
's7.img26.com',
's5.img26.com',
's3.img26.com',
's6.img26.com',
's2.img26.com',
's8.img26.com',
'store4.imghost.eu',
'www.mediafire.com',
'i.imgur.com',
'ist3-6.filesor.com',
'oi58.tinypic.com',
'oi60.tinypic.com',
'oi57.tinypic.com',
's2.xoimg.co',
'cdn.pornpics.com',
'imagetupian.nypd520.com',
'upics.ru',
'4.bp.blogspot.com',
'www.xoimg.club',
'3.bp.blogspot.com',
'1.bp.blogspot.com',
'2.bp.blogspot.com',
'pic.rmb.bdstatic.com',
'ww1.sinaimg.cn',
'5b0988e595225.cdn.sohucs.com',
'image.wowant.com',
'ww3.sinaimg.cn',
'ww4.sinaimg.cn',
'imgs.isocialkey.com',
'www.ratoo.net',
'nbvvv.8iwvsl.com',
'cdn.clickme.net',
'pic.sepapa.top',
'pic.bb164.com',
'www.kpd129.com',
'pic.xxappxx.xyz',
'www.52cjg.com',
's2b1t5v.8iwvsl.com',
'www.xiao88.top',
'image.ibb.co',
'c.pic303.com',
'img.76rb.com',
'www.freecnmove.com',
'img.pic123456.com',
'www.lcylpic.com',
'www.voxtu.com',
'pic.169rr.com',
'pic.4xtware.com',
'pic.99thingz.com',
'pic.212zx.com',
'baxgood.com',
'pic.043vb.com',
'mmslt1.com',
'185.153.180.20',
'95.214.113.122',
'95.214.113.46',
'img599.net',
'www.img599.net',
'c.share.photo.xuite.net',
'4.share.photo.xuite.net',
'www.playio1.com',
'lh3.googleusercontent.com',
'scontent-tpe1-1.xx.fbcdn.net',
'c1.staticflickr.com',
'images-blogger-opensocial.googleusercontent.com',
'img.xiatiantv.net',]


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
        num = parse(lines)
        if num == 10000:
            errorList.append(item)
    print errorList
    sys.exit()
