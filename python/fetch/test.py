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
    req = urllib2.Request(url, headers={'Cookie':'UM_distinctid=172f618d129281-055f55fad65761-47e1039-100200-172f618d12c2fb; ASPSESSIONIDCGTBTCBS=PMKJAEJDCEIHOGLMBCBGIGIA; ASPSESSIONIDCGQDTBDT=BGBOJDKDFAEGAAILGPKJOHOA; MAX_HISTORY={video:[{"name":"\u673A\u5173\u67AA\u56DA\u5F92","link":"http://www.tlyy.cc/dy/dy1/jiguanqiangqiutu/","pic":"https://pic.kssxdd.com/uploadimg/2020-6/20206249343540317.jpg"},{"name":"\u5E08\u7236","link":"http://www.tlyy.cc/dy/dy1/shifu/","pic":"https://pic.kssxdd.com/uploadimg/2015-12/201512140295682712.jpg"}]}; CNZZDATA4664080=cnzz_eid%3D1805056799-1593266144-https%253A%252F%252Fwww.baidu.com%252F%26ntime%3D1593271544; ASPSESSIONIDAERDRBDS=EMCIHLKDNJLPGOMGOJBGOHLF; ASPSESSIONIDAESDRADS=BGDFMLJDMFPAJIJOKKICJKFM; cscpvrich6565_fidx=3',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36', "Referer":url
                ,"Host": "wtsw28ah5a8q75g07ywb.lagoapps.com","Accept-Encoding": "gzip"})
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
   
#     videoId = re.compile("(.*\/)(\d+)\.html")
#     match = videoId.search('dongzuopian/202006/91671.html')
#     if match!=None:
#         
#         Id= match.group(2)
#         print match.group(1),Id
#         url  = 'vod-play-id-%s-src-1-num-1.html'%(Id)
#         print url
    soup= fetchUrl("https://wtsw28ah5a8q75g07ywb.lagoapps.com/vod/listing-0-0-0-0-0-0-0-0-0-1")
    print soup
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