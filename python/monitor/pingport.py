# -*- coding: utf-8 -*-
from common import db_ops
from common.envmod import *
import os
if __name__ == '__main__':
    dbVPN = db.DbVPN()
    ops = db_ops.DbOps(dbVPN)
    hosts = ops.getAllHost()
    for i in range(0, 1):
        for item in hosts:
            cmd = 'nc -u -n -v  %s -z %s ' % (item['gateway'],
                                              item['port'])
            print '---test ip--%s', item['gateway']
            os.popen(cmd)
        for item in hosts:
            cmd = 'ping -c 10 %s' % (item['gateway'])
            lines = os.popen(cmd).readlines()
#             print textlist
#             text = ''
#             for line in textlist:
#                 text = text + line
#             print text
#             if text.find('succeeded') > 0:
#                 pass
#             else:
#                 print item['gateway'], '---连不上，请检查'
