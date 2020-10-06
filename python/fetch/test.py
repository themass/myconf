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
    req = urllib2.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Linux; U; Android 8.0.0; zh-cn; HWI-AL00 Build/HUAWEIHWI-AL00) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30', "Referer":url
                ,"Host": "yepu.swapdox.com","Accept-Encoding": "gzip",
                "T-Token": "sPl1gaqimReMELUvMQ4s8w==","X-ONEX-AUTH":"" })
#     req.encoding = 'utf-8'
    response = urllib2.urlopen(req, timeout=3000)
    gzipped = response.headers.get(
        'Content-Encoding')  # 查看是否服务器是否支持gzip
    content = response.read().decode('utf8', errors='replace').replace("<![endif]-->","")
    return  BeautifulSoup(content)
if __name__ == '__main__':
    baseurl = "https://www.asy1000.com/"
    header = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl,
          "cookie":"Hm_lvt_64f3b8e72697945612104f755f0e6ce4=1557163354; __51cke__=; Hm_lpvt_64f3b8e72697945612104f755f0e6ce4=1557164611; __tins__19425543=%7B%22sid%22%3A%201557163355132%2C%20%22vd%22%3A%2010%2C%20%22expires%22%3A%201557166411669%7D; __51laig__=10",
          "X-Requested-With":"XMLHttpRequest"}
    str = '{"isdv":1,"type":5,"ispass":1,"url":"https://tv2.youkutv.cc/2020/08/29/BKdKI8YSVGmW5QPN/playlist.m3u8'
    content = str.replace('"', "").split("url:")
    shareVideo = re.compile(r"http(.*?)/2020/(.*?)")
    for text in content:
        print text
        match = shareVideo.search(text)
        if match!=None:
            print match.group(0),"-------",match.group(1),"-------",match.group(2)
#     videoId = re.compile("(.*\/)(\d+)\.html")
#     match = videoId.search('dongzuopian/202006/91671.html')
#     if match!=None:
#         
#         Id= match.group(2)
#         print match.group(1),Id
#         url  = 'vod-play-id-%s-src-1-num-1.html'%(Id)
#         print url
#     soup= fetchUrl("http://yepu.swapdox.com/api/ShortVideo/AddWahtchRecord/cak?newsId=c6d3d478-e65c-44cf-931f-5863074b7788")
#     print soup
    #print soup.findAll("div",{"class":"x3 margin-top"})
#     fcntl.flock('', fcntl.LOCK_EX)
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
#     str = '''
#     var vHLSurl    = "//"+avod+"/19/2018/07/LjVbWE7U/LjVbWE7U.m3u8";
#     '''
#     playVideo = re.compile(r'varvHLSurl="//"\+avod\+"(.*?)m3u8')
#     match = playVideo.search(str.replace(" ", ""))
#     print "%s%s%s"%("https://cdn.846u.com",match.group(1),"m3u8")