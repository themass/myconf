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

domainList=['4.share.photo.xuite.net',
'aimg.xyz',
'c.share.photo.xuite.net',
'cdn1.snapgram.co',
'cdn2.snapgram.co',
'cdn3.snapgram.co',
'cdn4.snapgram.co',
'cdn5.snapgram.co',
'd2.xse2018.com',
'img.76rb.com',
'img.pic123456.com',
'img.xiatiantv.net',
'is01.picsgonewild.com',
'opogx9ni8.bkt.clouddn.com',
's1bfd.df34d3f.com',
's1kbfd.df34d3f.com',
'www.52cjg.comhttp',
'www.eroti-cart.com',
'www.ttbcdn.com',
'www1.wi.to',]


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
