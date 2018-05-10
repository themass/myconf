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
from urllib import unquote
import sys
reload(sys)
sys.setdefaultencoding('utf8')
str1 = '''
<iframe width="640" height="360" src="https://weav.cc/embed/892fbfd1c5a5b457e577" frameborder="0" allowfullscreen></iframe>

'''

def fetchUrl(url):
    req = urllib2.Request(url, headers={'Cookie':"td_cookie=18446744069599001696; UM_distinctid=16267a77486203-0a34f7eb9f837-454c092b-1fa400-16267a7748726f; CNZZDATA4033785=cnzz_eid%3D1967344694-1522153663-null%26ntime%3D1522153663; CNZZDATA1263493226=2025093065-1522155903-null%7C1522155903; PHPSESSID=cqppj1tg9v8tf27j95ogqogjs1; td_cookie=18446744069599206493; WSKY=6c172; jiathis_rdc=%7B%22http%3A//www.zxdy.cc/vod/22266.html%22%3A1739039602%2C%22http%3A//www.zxdy.cc/play/22266-0-1.html%22%3A1739044927%2C%22http%3A//www.zxdy.cc/Uploads/https%3A//tupian.tupianzy.com/pic/upload/vod/2018-03-03/201803031520062617.jpg%22%3A1739118415%2C%22http%3A//www.zxdy.cc/list/1-p-3-0.html%22%3A1739129605%2C%22http%3A//www.zxdy.cc/list/1-p-1-0.html%22%3A1739216767%2C%22http%3A//www.zxdy.cc/list/9-p-1-0.html%22%3A1739358031%2C%22http%3A//www.zxdy.cc/list/9-p-2-0.html%22%3A1739371664%2C%22http%3A//www.zxdy.cc/Uploads/https%3A//wx3.sinaimg.cn/mw690/005w5c6ogy1fjuo496v5uj30tu15ok3k.jpg%22%3A1739577535%2C%22http%3A//www.zxdy.cc/Uploads/https%3A//img.alicdn.com/imgextra/i4/2264228004/TB2UynHnQqvpuFjSZFhXXaOgXXa_%21%212264228004.jpg%22%3A1739585958%2C%22http%3A//www.zxdy.cc/%22%3A1739586271%2C%22http%3A//www.zxdy.cc/vod/5128.html%22%3A1739763188%2C%22http%3A//www.zxdy.cc/vod/1.html%22%3A1739772004%2C%22http%3A//www.zxdy.cc/play/1-0-1.html%22%3A1739777508%2C%22http%3A//www.zxdy.cc/vod/4063.html%22%3A1739811363%2C%22http%3A//www.zxdy.cc/play/4063-0-2.html%22%3A1739820736%2C%22http%3A//www.zxdy.cc/list/11-p-1-0.html%22%3A1739855919%2C%22http%3A//www.zxdy.cc/vod/22236.html%22%3A0%7C1522158279843%2C%22http%3A//www.zxdy.cc/play/22236-0-1.html%22%3A%220%7C1522158307282%22%7D",
                'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13', "Referer":url})
    req.encoding = 'utf-8'
    response = urllib2.urlopen(req, timeout=300)
    gzipped = response.headers.get(
        'Content-Encoding')  # 查看是否服务器是否支持gzip
    content = response.read().decode('utf8', errors='replace')
    print content
if __name__ == '__main__':
    fetchUrl("http://zanquye.com")
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
    #     s = '[12.19] 公司里的巨乳少妇搞来玩一玩[12P]'
    #     img_channel_title = re.compile(r"\[[0-9]+P\]")
    #     img_channel_date = re.compile(r"\[[0-9\.]+\]")
    #     match = img_channel_title.search(s)
    #     print match.group(0)
    #     match = img_channel_date.search(s)
    #     print match.group(0)
#     regVideo = re.compile(r'src="(.*)" frameborder=')
#     match = regVideo.search(str1)
#     print match.group(1)
    
#     str = "mac_from='Aplayer',mac_server='',mac_note='',mac_url=unescape('%u5f00%u59cb%u64ad%u653e%24http%3A%2F%2Fvideo.jiagew762.com%3A8091%2F20180106%2F7G8ixAL1%2Findex.m3u8'); "
#     regVideo = re.compile(r"mac_url=unescape\('(.*)(http)(.*)'\);")
#     match = regVideo.search(str)
#     str2 = '(.*)'
#     str = '''
# var mac_flag='play',mac_link='/g/41818/{src}/{num}.html', mac_name='速度与激情8',mac_from='m3u8',mac_server='no',mac_note='',mac_url=unescape('HD1280%u9ad8%u6e05%u4e2d%u5b57%u97e9%u7248$http://fuli.yazyzw.com/20170603/XgwO7tMy/index.m3u8#BD1280%u9ad8%u6e05%u4e2d%u82f1%u53cc%u5b57%u7248$http://hao.zuida-youku.com/20170609/NoFPAsy5/index.m3u8');
# ''' 
#     videoApi = re.compile(r"http(.*)\.m3u8")
#     match = videoApi.search(str)
#     print match
#     print match.group(1).replace("')","")
#     print unquote(str)