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
reload(sys)
#
sys.setdefaultencoding('utf8')
reload(sys)
import subprocess


# 9226688.com 8182277.com 8283377.com qqav10.com qqav9.com qqav8.com qqav7.com qqav6.com qqav5.com 
baseurl = "https://xiaoyakankan.com"
header = {
    'User-Agent': 'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html）Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Cookie': 'Hm_lvt_a7dbcd0d5fd2dbdc43e5060c94acaa09=1527844837; PHPSESSID=g8ueibtojgjuub262ae109m2j1; Hm_lvt_c0060128b5e4b5b38a10be83f06960fd=1530951178; msvod_from_url=CXHdyI37jSHtNtnU%2FGBkOiMfjYp75b9bAMxJauXJEbCph8pO90GzNwM; msvod_user_id=sTLyUSP2KKex0l%2FenE0; msvod_user_login=0BUv%2FRmatXLtwy8ku6E2s8cfhsoQfkASdur2QcWy8wZb0twm3WRbkA; msvod_pl_token=A_FO9jJ79ZZkyVFTBxw1KLmX; Hm_lpvt_c0060128b5e4b5b38a10be83f06960fd=1530951284; msvod_token=_pF0%2FpHf%2FPEKXfOFQGGwSyOE',
    'Referer': baseurl,
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1'
}
maxCount = 3
regVideo = re.compile(r'"http(.*?)\.m3u8')
namereg = re.compile(r"(&#[0-9]*;)+")

class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url):
        count = 0
        while count < maxCount:
            try:
                curl_command = [
                    'curl', baseurl+url,
                    '-H', 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    '-H', 'accept-language: zh-CN,zh;q=0.9',
                    '-H', 'cache-control: no-cache',
                    '-H', 'cookie: _ga=GA1.1.611983894.1716478735; __PPU_puid=7372220048289729256; UGVyc2lzdFN0b3JhZ2U=%7B%22CAIFRQ%22%3A%22ACZSQQAAAAAAAAAB%22%2C%22CAIFRT%22%3A%22ACZSQQAAAABncNdQ%22%2C%22MTIFRQ%22%3A%22ADO5uwAAAAAAAAAB%22%2C%22MTIFRT%22%3A%22ADO5uwAAAABncNdQ%22%7D; bnState_1871751={"impressions":1,"delayStarted":0}; hid=b3ac650730881e9e1d5c5e073b89d300; _ga_ECF2QFGQ9G=GS1.1.1735994610.15.0.1735994610.0.0.0; cf_clearance=qskGiffzDuD6YFS3fYw6VdzsMo62HfZLvHUd8vCa3yw-1735994615-1.2.1.1-i8ytuvtyOniXQwBOHj1sTCEqgJU28xNsscFIXmFprG.sDMDRn3NpQDby4RTdRpZF_8o0oIwe1Vn0wGQ2pyihrYemg1Wq7v8st6WBMk9UPvTDyCbcoz_9.VscKhyL87nhexF.X30I.WURRn3LVTo3BjpOUzL.kOXS4j2oqsONhvks34YptqG6NOdMtCyo2dJhcCojSK9QUqU9mJQWqDfpdItC4QBuiwtYrfj9epV8JGkB8z3zUwutPpVbWSRyZ8MeySljHA5U5yoXZhzeu1DilpnAXoiYZaXoOwE0WY4nT_zqGWBl8pEHQq4bp.ryc2AWVy3BhrYDnZZ2BlDnWpYXOc34Ata0UIbPcPJxnWrbiB9BoYgqpchaPYTzGlTiIqnJxvOB_O9MEJayWBNtNpLm2Q',
                    '-H', 'pragma: no-cache',
                    '-H', 'priority: u=0, i',
                    '-H', 'sec-ch-ua: "Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                    '-H', 'sec-ch-ua-arch: "arm"',
                    '-H', 'sec-ch-ua-bitness: "64"',
                    '-H', 'sec-ch-ua-full-version: "131.0.6778.86"',
                    '-H', 'sec-ch-ua-full-version-list: "Google Chrome";v="131.0.6778.86", "Chromium";v="131.0.6778.86", "Not_A Brand";v="24.0.0.0"',
                    '-H', 'sec-ch-ua-mobile: ?0',
                    '-H', 'sec-ch-ua-model: ""',
                    '-H', 'sec-ch-ua-platform: "macOS"',
                    '-H', 'sec-ch-ua-platform-version: "14.3.0"',
                    '-H', 'sec-fetch-dest: document',
                    '-H', 'sec-fetch-mode: navigate',
                    '-H', 'sec-fetch-site: none',
                    '-H', 'sec-fetch-user: ?1',
                    '-H', 'upgrade-insecure-requests: 1',
                    '-H', 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
                ]

                # 执行 curl 命令
                process = subprocess.Popen(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                soup = BeautifulSoup(stdout)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', baseurl + url, '次数', count
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
        with open("xiaoyakankan/header.html") as f:
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
        with open("xiaoyakankan/header2.html") as f:
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

    