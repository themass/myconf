#!/usr/bin python
# -*- coding: utf-8 -*-
from common import *
from common.envmod import *
from common import db_ops
import sys
import time
reload(sys)
sys.setdefaultencoding('utf8')
url = 'http://ip.taobao.com/service/getIpInfo.php'
headers = {'User-Agent':
           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": "https://www.baidu.com"}


def getLocal(ip, id):
    param = {'ip': ip}
    ret = httputil.getData(url, param, headers)
    obj = {}
    obj['id'] = id
    if ret['code'] == 0:
        data = ret.get('data', {})
        obj['local'] = data.get(
            'country') + '-' + data.get('city') + '-' + data.get('isp')
        print 'ip=', ip, ' ;local=', obj['local']
    else:
        obj['local'] = ''
    return obj
if __name__ == '__main__':
    dbVPN = db.DbVPN()
    ops = db_ops.DbOps(dbVPN)
    rows = ops.getAllwannaIplocalnull()
    print 'need update len=', len(rows)
    objs = []
    for row in rows:
        item = getLocal(row['ip'], row['id'])
        objs.append(item)
        time.sleep(1)
    ops.updateWannaIpLocal(objs)
    #getLocal('223.72.96.151', 1)
