#!/usr/bin python
# -*- coding: utf-8 -*-
from common import *
from common.envmod import *
from common import db_ops
import sys
reload(sys)
sys.setdefaultencoding('utf8')
url = 'http://ip.taobao.com/service/getIpInfo.php?ip=%s'


def getLocal(ip, id):
    ret = httputil.getData(url % (ip))
    obj = {}
    obj['id'] = id
    if ret['code'] == 0:
        data = ret.get('data', {})
        obj['local'] = data.get(
            'country') + '-' + data.get('city') + '-' + data.get('isp')
    else:
        obj['local'] = ''
    return obj
if __name__ == '__main__':
    dbVPN = db.DbVPN()
    ops = db_ops.DbOps(dbVPN)
    rows = ops.getAllwannaIplocalnull()
    objs = []
    for row in rows:
        item = getLocal(row['ip'], row['id'])
        objs.append(item)
    ops.updateWannaIpLocal(objs)
