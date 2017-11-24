#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
import threading
from BeautifulSoup import BeautifulSoup
from common.envmod import *
from common import common
from common import typeutil
from common import db_ops
from common import MyQueue
from common import dateutil
from common import html_parse
import re
import os
import sys
import json
reload(sys)
str1 = '''
{
"success":true,
"total":20,
"msg":""
}
'''
if __name__ == '__main__':
    #     name = '第95期<!--[if lt IE 9 ]><![endif]-->2017/9/9<!--[if lt IE 9 ]><![endif]-->'
    #     strName = name.replace(
    #         "<!--[if lt IE 9 ]>", "").replace("<![endif]-->", "")
    #     name = html_parse.filter_tags(strName)
    #     print name

    str = '''
     <div id="pages">页次：1/138&nbsp;每页25&nbsp;总数3428&nbsp;&nbsp;&nbsp;&nbsp;首页&nbsp;&nbsp;上一页&nbsp;&nbsp;<a href='/html/article/mingxing/index_2.html'>下一页</a>&nbsp;&nbsp;<a href='/html/article/mingxing/index_138.html'>尾页</a>&nbsp;&nbsp;&nbsp;&nbsp;转到:&nbsp;&nbsp;<input type="input" name="page" id="page" size=4 class="pagego"/><input type="button" value="跳 转" onclick="window.location='/html/article/mingxing/index_<{page}>.html'.replace('<{page}>', document.getElementById('page').value);" class="pagebtn" /></div>
    '''
    soup = BeautifulSoup(str)
    reg = re.compile(r"(.*)index_\d+\.html")
    divs = soup.findAll("div", {"id": "pages"})
    if len(divs) > 0:
        aAll = divs[len(divs) - 1].findAll("a")
        for a in aAll:
            if a.text.count(u"尾页") > 0:
                href = a.get('href')
                print href
    url = '/html/article/mingxing/index_138.html'
    match = reg.search(url)
    print match.group(1)
