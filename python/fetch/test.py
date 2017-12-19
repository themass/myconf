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
from urlparse import urlparse
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

    #     str = '''dsdasdsa
    # <div id="pages"><a title="Page">&nbsp;<b>3</b>/<b>9</b> </a>&nbsp;&nbsp;<a href="/html/article/jiqing/2017/0612/397928.html">首页</a>&nbsp;<a href="/html/article/jiqing/2017/0612/397928_2.html">上一页</a>&nbsp;<a href="/html/article/jiqing/2017/0612/397928.html">1</a>&nbsp;<a href="/html/article/jiqing/2017/0612/397928_2.html">2</a>&nbsp;<b>3</b>&nbsp;<a href="/html/article/jiqing/2017/0612/397928_4.html">4</a>&nbsp;<a href="/html/article/jiqing/2017/0612/397928_5.html">5</a>&nbsp;<a href="/html/article/jiqing/2017/0612/397928_6.html">6</a>&nbsp;<a href="/html/article/jiqing/2017/0612/397928_4.html">下一页</a>&nbsp;<a href="/html/article/jiqing/2017/0612/397928_9.html">尾页</a></div>
    #            </div>dasDASDA</div></div></div></div>
    #     '''
    #     soup = BeautifulSoup(str)
    #     reg = re.compile(r"(.*)index(.*)\.html")
    #     divs = soup.findAll("div", {"id": "pages"})
    #     if len(divs) > 0:
    #         aAll = divs[len(divs) - 1].findAll("a")
    #         for a in aAll:
    #             if a.text.count(u"尾页") > 0:
    #                 href = a.get('href')
    #                 print href
    #     url = '/html/article/mingxing/index.html'
    #     match = reg.search(url)
    #     print match.group(2)
    #     regPage = re.compile(r'<div id="pages">(.*)</div>')
    #     match = regPage.search(str)
    #     print match.group(1)
    #     url = 'http://113.215.20.136:9011/113.215.6.77/c3pr90ntcya0/youku/6981496DC9913B8321BFE4A4E73/0300010E0C51F10D86F80703BAF2B1ADC67C80-E0F6-4FF8-B570-7DC5603F9F40.flv'
    #     pattern = 'http://(.*?):9011/'
    #     out = re.sub(pattern, 'http://127.0.0.1:9091/', url)
    #     print out
    #     url_str = "http://www.163.com/mail/index.htm"
    #     url = urlparse(url_str)
    #     print 'protocol:', url.scheme
    #     print 'hostname:', url.hostname
    #     print 'port:', url.port
    #     print 'path:', url.path
    s = '[12.19] 公司里的巨乳少妇搞来玩一玩[12P]'
    img_channel_title = re.compile(r"\[[0-9]+P\]")
    img_channel_date = re.compile(r"\[[0-9\.]+\]")
    match = img_channel_title.search(s)
    print match.group(0)
    match = img_channel_date.search(s)
    print match.group(0)
