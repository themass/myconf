# -*- coding: utf-8 -*-
from common import db_ops
from common.envmod import *
import os
import re
reg = re.compile(
    r"rtt min/avg/max/mdev = ([1-9\.]+)/([1-9\.]+)/([1-9\.]+)")


def parse(pingtext):
    match = reg.search(pingtext)
    print match
    if match == None:
        return 10000
    return match.group(2)
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
        cmd = 'ping  -c2 -w2 %s' % (item['gateway'])
        lines = os.popen(cmd).readlines()
        num = int(parse(lines[len(lines) - 1]))
        print 'ip: %s --------cost %s' % (item['gateway'], num)
