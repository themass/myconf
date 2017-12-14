# -*- coding: utf-8 -*-
from common import db_ops
from common.envmod import *
import os
import re
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
        cmd = 'ping  -c2 -w2 %s' % (item['gateway'])
        lines = os.popen(cmd).readlines()
        num = parse(lines)
        print 'ip: %s --------cost %s' % (item['gateway'], num)
