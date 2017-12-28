# -*- coding: utf-8 -*-
from common import db_ops
from common import httputil
from common.envmod import *
import os
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
reg = re.compile(
    r"rtt min/avg/max/mdev = ([0-9\.]+)/([0-9\.]+)/([0-9\.]+)")

url = 'http://api.sspacee.com/vpn/api/noapp/ping.json'


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
                errorList.append("%s:%s" % (item['gateway'], -1))
            else:
                print '公司：【%-15s】----国家：【%s】------ip: 【%-15s】 --------可用了，请检查 cost:【%-15s】' % (item['com'], myAlign(item['cname'], 7), item['gateway'], num)
                errorList.append("%s:%s" % (item['gateway'], 1))
        else:
            print '公司：【%-15s】----国家：【%s】------ip: 【%-15s】 --------cost:【%-15s】' % (item['com'], myAlign(item['cname'], 7), item['gateway'], num)
            if num == 10000:
                errorList.append("%s:%s" % (item['gateway'], -1))
            else:
                errorList.append("%s:%s" % (item['gateway'], 0))
    if len(errorList) > 0:
        str = ';'.join(errorList)
        print str
        data = {}
        data['pingCheck'] = str
        print httputil.postRequestWithParam(url, data, {})
#         emailutil.sendEmailShell(
#             ["liguoqing19861028@163.com"], "VPS-check-error",  ''.join(errorList))
#     if len(okList) > 0:
#         emailutil.sendEmailShell(
#             ["liguoqing19861028@163.com"], "VPS-check-ok",  ''.join(okList))
    sys.exit()
