#!/usr/bin python
# -*- coding: utf-8 -*-
from urlparse import urlparse
from common import common
import time
from common.envmod import *
from common import db_ops
from common import httputil

IP_HOST="http://ip.taobao.com/service/getIpInfo.php?ip="
if __name__ == '__main__':
    dbVPN = db.DbVPN()
    ops = db_ops.DbOps(dbVPN)
    objs = ops.selectDevInfoIpNull()
    for item in objs:
        ret =httputil.getData(IP_HOST+item.get("ip"), {}, {}) 
        print ret.get("data",{}).get("country",None),item.get("ip")
        if ret.get("data",{}).get("country",None)!=None:
            item['loc']=ret.get("data",{}).get("country")
    ops.updateDevinfoLoc(objs)
    dbVPN.commit()
    dbVPN.close()

