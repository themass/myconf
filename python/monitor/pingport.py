# -*- coding: utf-8 -*-
from common import db_ops
from common.envmod import *
import os
import re
reg = re.compile(r"time=(\d+)")


def parse(pingtext):
    match = reg.search(pingtext)
    if match == None:
        return 10000
    return match.group(1)
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
        cmd = 'ping  -c 5 %s' % (item['gateway'])
        lines = os.popen(cmd).readlines()
        count = 0
        for line in lines[1:len(lines)]:
            num = int(parse(line))
            count = count + num
        print 'ip: %s --------cost %s' % (item['gateway'], count / 5)
