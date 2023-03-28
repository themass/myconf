#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
import zlib
import urllib2
import threading
import json
import subprocess
from common.envmod import *
from common import db_ops
from common import common
import threading
from BeautifulSoup import BeautifulSoup
import re
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def fetchUrl(url):
    try:
        req = urllib2.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13', "Referer":"https://git.corp.kuaishou.com"
        ,'cookie':'event_filter=all; sidebar_collapsed=false; _gitlab_session=d75443fed205684349937488b24e1aed; apdid=f55e3b2a-c8d0-4a7f-a2a2-d046246c22b8e7dd6977120f91fe5f524a4598eafd4c:1679653005:1; _did=web_69014337109301C4; hdige2wqwoino=MEQmynetKerAbGJzEsKBfN462JmPPaBn12dcc4eb; adm-did=Rz7eL0bgtc9fmEVkgs_ltc4wsJeBF9PFfnTDtQwmGu6Kb2zFwkRmgCJvkQp0EQ0i'})
        req.encoding = 'utf-8'
        response = urllib2.urlopen(req, timeout=300)
        gzipped = response.headers.get(
            'Content-Encoding')  # 查看是否服务器是否支持gzip
        content = response.read().decode('utf8', errors='replace')
        if gzipped:
            content = zlib.decompress(
                content, 16 + zlib.MAX_WBITS)  # 解压缩，得到网页源码
        return content
    except Exception as e:
        print common.format_exception(e)
        print '打开页面错误,重试'

def printgit():
    names= []
    for i in range(1, 6):
        url = '%s%s'%('https://git.corp.kuaishou.com/groups/audit/-/children.json?page=',i)
        content = fetchUrl(url)
        objList = json.loads(content)
        for item in objList:
            name = '%s%s'%('git clone https://git.corp.kuaishou.com',item.get('relative_path'))
            print name
            names.append(item.get('relative_path').replace('/audit/',''))
    return names
def mvninstall():
    names = printgit()
    for name in names:
        path = '%s%s'%('/Users/gqli/work/ks/',name)
        cmd1 = '%s%s'%("cd ",path)
        cmd2 = 'mvn install'
        cmd = cmd1 + " && " + cmd2
        subprocess.call(cmd,shell=True)

if __name__ == '__main__':
    mvninstall()