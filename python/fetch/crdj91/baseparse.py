#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import zlib
import time
import urllib2
import threading
from common.envmod import *
from common import db_ops
from common import common
import threading,os
from BeautifulSoup import BeautifulSoup
import re,sys
import subprocess
import shlex
reload(sys)
#
import cloudscraper
sys.setdefaultencoding('utf8')

# 9226688.com 8182277.com 8283377.com qqav10.com qqav9.com qqav8.com qqav7.com qqav6.com qqav5.com 
baseurl = "https://91crdj.com/"
header = {'User-Agent':
          'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html）Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)', 
          'Cookie':'_ga=GA1.1.1987535338.1790184089; _ym_uid=1790184090227697502; _ym_d=1790184090; _ym_isad=2; _ym_visorc=w; _ga_NRW7S9SLR5=GS2.1.s1790184088$o1$g1$t1790186817$j60$l0$h0'
          ,"Referer": baseurl}
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36',
}
cookies = {
    "_ga": "GA1.1.1987535338.1790184089",
    "_ym_uid": "1790184090227697502",
    "_ym_d": "1790184090",
    "_ym_isad": "2",
    "_ym_visorc": "w",
    "_ga_NRW7S9SLR5": "GS2.1.s1790184088$o1$g1$t1790187060$j60$l0$h0"
}
maxCount = 1
regVideo = re.compile(r'http(.*?)m3u8"')
namereg = re.compile(r"(&#[0-9]*;)+")

class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url):
        count = 0
        # scraper = cloudscraper.create_scraper()
        while count < maxCount:
            try:
                # resp = scraper.get(baseurl+url, headers=headers, cookies=cookies, timeout=30)
                # req = urllib2.Request( url, headers=header)
                # req.encoding = 'utf-8'
                # response = urllib2.urlopen(req, timeout=3000)
                # gzipped = response.headers.get(
                #     'Content-Encoding')  # 查看是否服务器是否支持gzip
                # content = response.read().decode('utf-8', errors='replace')
                # if gzipped:
                #     content = zlib.decompress(
                #         content, 16 + zlib.MAX_WBITS)  # 解压缩，得到网页源码
                    # ========= 可配置变量 =========
                curl_args = [
                    "curl",
                    "--url", url,
                    "-H", 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    "-H", 'accept-language: zh-CN,zh;q=0.9,en;q=0.8',
                    "-H", 'cache-control: no-cache',
                    "-H", '_ga=GA1.1.1987535338.1790184089; _ym_uid=1790184090227697502; _ym_d=1790184090; _ym_isad=2; _ym_visorc=w; _ga_NRW7S9SLR5=GS2.1.s1790184088$o1$g1$t1790187060$j60$l0$h0',
                    "-H", 'pragma: no-cache',
                    "-H", 'priority: u=0, i',
                    "-H", 'referer: %s' % baseurl,
                    "-H", 'sec-ch-ua: "Google Chrome";v="153", "Not_A Brand";v="8", "Chromium";v="153"',
                    "-H", 'sec-ch-ua-mobile: ?0',
                    "-H", 'sec-ch-ua-platform: "macOS"',
                    "-H", 'sec-fetch-dest: document',
                    "-H", 'sec-fetch-mode: navigate',
                    "-H", 'sec-fetch-site: same-origin',
                    "-H", 'sec-fetch-user: ?1',
                    "-H", 'upgrade-insecure-requests: 1',
                    "-H", 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36',
                ]
                p = subprocess.Popen(curl_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = p.communicate()
                html = stdout.decode('utf8','ignore')
                soup = BeautifulSoup(html)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1
                time.sleep(1)

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')

    def fetchUrlWithBase(self, url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(url, headers=header)
                content = urllib2.urlopen(req, timeout=300).read()
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1
                time.sleep(1)

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')
    def header(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("crdj91/header.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        print content
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def fetchContentUrlWithBase(self, url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(url, headers=header)
                content = urllib2.urlopen(req, timeout=300).read()
                return content
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1
                time.sleep(1)

        print '打开页面错误,重试3次还是错误', url
        return ''

    