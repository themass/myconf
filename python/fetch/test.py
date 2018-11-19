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
from common import httputil
import requests  
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
    return content
if __name__ == '__main__':
#     baseurl = "http://www.fuli750.com/api/payvideo.html"
#     header = {'User-Agent':
#           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl,
#           "cookie":"__cfduid=daf97951d263f43b40aa880057d128ec61534232909; PHPSESSID=df01o1psnjpnr67df4k4q53s50; UM_distinctid=1653768772b33e-00e6b1d3653486-47e1039-1fa400-1653768772c5f; CNZZDATA1274203680=1684804072-1534228697-%7C1534234099",
#           "X-Requested-With":"XMLHttpRequest"}
#     data = {}
#     data['id']="1844"
#     ret = httputil.postRequestWithParam("http://www.fuli750.com/api/payvideo.html", data, header)
#     print ret
#     dbVPN = db.DbVPN()
#     ops = db_ops.DbOps(dbVPN)
#     obj = {}
#     obj['url'] = 'https://520cc.club/embed/136726.mp4'
#     obj['pic'] = ''
#     obj['name'] = 'test520ccwebview'
#     obj['path'] = 'test520ccwebview'
#     obj['updateTime'] = datetime.datetime.now()
#     obj['channel'] = 'test'
#     obj['videoType'] = "fanqiang"
#     obj['baseurl'] = 'https://520cc.club'
#     ops.inertVideo(obj,'webview','https://520cc.club','fanqiang')
#     
#     obj['url'] = 'https://1fgm8js.oloadcdn.net/dl/l/bwM0AoKhnaKk1_II/F9ESsEd1Qw0/5b7056b1da6d3.mp4?mime=true'
#     obj['pic'] = ''
#     obj['name'] = 'test520ccnormal'
#     obj['path'] = 'test520ccnormal'
#     obj['updateTime'] = datetime.datetime.now()
#     obj['channel'] = 'test'
#     obj['videoType'] = "fanqiang"
#     obj['baseurl'] = 'https://520cc.club'
#     ops.inertVideo(obj,'normal','https://520cc.club','fanqiang')
# 
#     dbVPN.commit()
#     dbVPN.close()
#     regVideo = re.compile(r'getmovurl\.html", {id:(.*?),td:(.*?)},')
#     str = '$.post("/index/getmovurl.html", {id:15699,td:2},'
#     match = regVideo.search(str)
#     print match.group(1),match.group(2)
#     iframeVideo = re.compile(r"onclick=\"window.open\('magnet(.*?)','_self'\)")
#     str = "str: \"<tr onmouseover=\"this.style.backgroundColor='#F4F9FD';this.style.cursor='pointer';\" onmouseout=\"this.style.backgroundColor='#FFFFFF'\" height=\"35px\" style=\"border-top: 1px solid rgb(221, 221, 221); background-color: rgb(255, 255, 255); cursor: pointer;\">\r\n    <td width=\"70%\" onclick=\"window.open('magnet:?xt=urn:btih:C05D741E9F2CC7E991E06FAB854136584763B78E&dn=DIC-017_CAVI','_self')\">\r\n        <a style=\"color:#333\" rel=\"nofollow\" title=\"滑鼠右鍵點擊並選擇【複製連結網址】\" href=\"magnet:?xt=urn:btih:C05D741E9F2CC7E991E06FAB854136584763B78E&dn=DIC-017_CAVI\">DIC-017_CAVI  字幕<\/a>\r\n            <\/td>\r\n    <td style=\"text-align:center;white-space:nowrap\" onclick=\"window.open('magnet:?xt=urn:btih:C05D741E9F2CC7E991E06FAB854136584763B78E&dn=DIC-017_CAVI','_self')\">\r\n        <a style=\"color:#333\" rel=\"nofollow\" title=\"滑鼠右鍵點擊並選擇【複製連結網址】 href=\"magnet:?xt=urn:btih:C05D741E9F2CC7E991E06FAB854136584763..."
#     match = iframeVideo.search(str)
#     print match,match.group(1)
#     regVideo = re.compile(r"encrypt\((.*), 'E', \$key\);")
#     str = "$play=encrypt(https://youku.cdn-tudou.com/20180508/5819_7b1f8025/index.m38, 'E', $key);"
#     match = regVideo.search(str)
#     print matc
#     print os.popen("wget http://api.ourder.com:8080/video/ssl/player.aspx?c=0515055a4c1e494f494e&w=640&h=400").read()
#     driver = webdriver.Chrome()
#     driver.get("http://api.ourder.com:8080/video/ssl/player.aspx?c=0515055a4c1e494f494e&w=640&h=400")
#     print driver.page_source
#     print requests.get("http://api.ourder.com:8080/video/ssl/player.aspx?c=0515055a4c1e494f494e&w=640&h=400").text
    str = '''
    var vHLSurl    = "//"+avod+"/19/2018/07/LjVbWE7U/LjVbWE7U.m3u8";
    '''
    playVideo = re.compile(r'varvHLSurl="//"\+avod\+"(.*?)m3u8')
    match = playVideo.search(str.replace(" ", ""))
    print "%s%s%s"%("https://cdn.846u.com",match.group(1),"m3u8")