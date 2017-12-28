# -*- coding: utf-8 -*-
from common import db_ops
from common import emailutil
from common.envmod import *
import os
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
reg = re.compile(
    r"rtt min/avg/max/mdev = ([0-9\.]+)/([0-9\.]+)/([0-9\.]+)")


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
    dbVPN = db.DbVPN()
    ops = db_ops.DbOps(dbVPN)
    hosts = ops.getAllHost()
    #     for i in range(0, 1):
    #         for item in hosts:
    #             cmd = 'nc -u -n -v  %s -z %s ' % (item['gateway'],
    #                                               item['port'])
    #             print '---test ip--%s', item['gateway']
    #             os.popen(cmd)
    errorList = []
    okList = []
    for item in hosts:
        #         if item['enable'] == 0:
        #             print '公司：【%-15s】----国家：【%s】------ip: 【%-15s】 --------不可用' % (item['com'], myAlign(item['cname'], 7), item['gateway'])
        #             continue

        cmd = 'ping  -c2 -w2 %s' % (item['gateway'])
        lines = os.popen(cmd).readlines()
        num = parse(lines)
        if item['enable'] == 0:
            if num == 10000:
                print '公司：【%-15s】----国家：【%s】------ip: 【%-15s】 --------不可用' % (item['com'], myAlign(item['cname'], 7), item['gateway'])
            else:
                print '公司：【%-15s】----国家：【%s】------ip: 【%-15s】 --------可用了，请检查 cost:【%-15s】' % (item['com'], myAlign(item['cname'], 7), item['gateway'], num)
                okList.append(item['gateway'])
        else:
            print '公司：【%-15s】----国家：【%s】------ip: 【%-15s】 --------cost:【%-15s】' % (item['com'], myAlign(item['cname'], 7), item['gateway'], num)
        if num == 10000 and item['enable'] != 0:
            errorList.append(item['gateway'])
    if len(errorList) > 0:
        emailutil.send_mail(
            ["liguoqing19861028@163.com"], "VPS-check-error",  ''.join(errorList))
    if len(okList) > 0:
        emailutil.send_mail(
            ["liguoqing19861028@163.com"], "VPS-check-ok",  ''.join(okList))
