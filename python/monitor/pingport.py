# -*- coding: utf-8 -*-
from common import db_ops
from common.envmod import *
import os
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
reg = re.compile(
    r"rtt min/avg/max/mdev = ([0-9\.]+)/([0-9\.]+)/([0-9\.]+)")


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
    for item in hosts:
        if item['enable'] == 0:
            print '公司：【%s】----国家：【%s】------ip: 【%s】 --------不可用' % (item['com'], item['cname'], item['gateway'])
            continue

        cmd = 'ping  -c2 -w2 %s' % (item['gateway'])
        lines = os.popen(cmd).readlines()
        num = parse(lines)
        print '公司：【%s】----国家：【%s】------ip: 【%s】 --------cost:【%s】' % (item['com'], item['cname'], item['gateway'], num)
