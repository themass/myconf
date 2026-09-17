#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import zlib
import urllib2
import threading
from common.envmod import *
from common import db_ops
from common import common
import threading,os
from BeautifulSoup import BeautifulSoup
import re,sys
import time
import cloudscraper
reload(sys)
# 
sys.setdefaultencoding('utf8')

# 9226688.com 8182277.com 8283377.com qqav10.com qqav9.com qqav8.com qqav7.com qqav6.com qqav5.com 
baseurl = "https://rfd0i4.jstv800.com"
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
    "_ym_uid": "1726938050509318806",
    "_ga": "GA1.1.1936408816.1742034872",
    "_ym_d": "1774863920",
    "JSESSIONID": "b10acca8b75dccd7a46bf6a9c60d6423",
    "server_name_session": "ec44f6c16c76e0924f0daf80e2310a1a",
    "wms": "1",
    "_ym_visorc": "b",
    "_ym_isad": "2",
    "_ga_F8MXJQGLN1": "GS2.1.s1789657694$o20$g1$t1789657905$j60$l0$h882662573",
    "cf_clearance": "etjZO.BHnEJW2ApwaQGq_XbHYKJmZxsWGjZKLxXMZzI-1789657905-1.2.1.1-_4b6hEp.MgKNq6T7WWcA2mNakQ8zL3QwFvuS6qpc99Z.MHw7Q_sI.jgEcefEV60gqGWjn5XejgjrmP4SlQj9HNL41m6CE4XDKbBH3qtu9GZgAMuZYqejOMQ5HEyDvodGMNVEtinGL8prtnUDFJe2ufN5dW1bJxLKpkM0PZLtFsdkDacriz2CyhCB1GOhJrmh98pbkiAXDzaFbqG1QPnFISrxFUnbNrgRLo2eQOy0YuwQqnoIywPMdxZCOlmZl7iqkano1rqw1HcOBeITD.RvwQG50pSkwXEZI35AVkByUd4CX5LvFhTZcXdIOpCQc1I4uEniQNlaDEzkrFuCQZOl5gvt7cnHmn9YzjWelljGXBU"
}
maxCount = 3
regVideo = re.compile(r"http(.*?)m3u8")
namereg = re.compile(r"(&#[0-9]*;)+")

class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url):
        scraper = cloudscraper.create_scraper()
        count = 0
        while count < maxCount:
            try:
                resp = scraper.get(baseurl+url, headers=headers, cookies=cookies, timeout=30)
                # req = urllib2.Request(baseurl + url, headers=header)
                # req.encoding = 'utf-8'
                # response = urllib2.urlopen(req, timeout=3000)
                # gzipped = response.headers.get(
                #     'Content-Encoding')  # 查看是否服务器是否支持gzip
                # content = response.read().decode('utf-8', errors='replace')
                # if gzipped:
                #     content = zlib.decompress(
                #         content, 16 + zlib.MAX_WBITS)  # 解压缩，得到网页源码
                soup = BeautifulSoup(resp.text)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', baseurl + url, '次数', count
                count = count + 1
                time.sleep(1)

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')

    def header(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("porn91/header.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        print content
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def header3(self):
        #         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__))
        with open("porn91/header3.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        print content
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def header2(self):
        #         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__))
        with open("porn91/header2.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        print content
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist

    