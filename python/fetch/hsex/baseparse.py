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
import re,sys,signal
import time
reload(sys)
import subprocess
from feach import CurlFetcher

# 
sys.setdefaultencoding('utf8')

# 9226688.com 8182277.com 8283377.com qqav10.com qqav9.com qqav8.com qqav7.com qqav6.com qqav5.com 
baseurl = "https://hsex.men/"
header = {'User-Agent':
          'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html）Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)', 
          'Cookie':'cookie: _ga=GA1.1.611983894.1716478735; __PPU_puid=7372220048289729256; UGVyc2lzdFN0b3JhZ2U=%7B%22CAIFRQ%22%3A%22ACZSQQAAAAAAAAAB%22%2C%22CAIFRT%22%3A%22ACZSQQAAAABncNdQ%22%2C%22MTIFRQ%22%3A%22ADO5uwAAAAAAAAAB%22%2C%22MTIFRT%22%3A%22ADO5uwAAAABncNdQ%22%7D; bnState_1871751={"impressions":1,"delayStarted":0}; hid=b3ac650730881e9e1d5c5e073b89d300; _ga_ECF2QFGQ9G=GS1.1.1735994610.15.0.1735994610.0.0.0; cf_clearance=qskGiffzDuD6YFS3fYw6VdzsMo62HfZLvHUd8vCa3yw-1735994615-1.2.1.1-i8ytuvtyOniXQwBOHj1sTCEqgJU28xNsscFIXmFprG.sDMDRn3NpQDby4RTdRpZF_8o0oIwe1Vn0wGQ2pyihrYemg1Wq7v8st6WBMk9UPvTDyCbcoz_9.VscKhyL87nhexF.X30I.WURRn3LVTo3BjpOUzL.kOXS4j2oqsONhvks34YptqG6NOdMtCyo2dJhcCojSK9QUqU9mJQWqDfpdItC4QBuiwtYrfj9epV8JGkB8z3zUwutPpVbWSRyZ8MeySljHA5U5yoXZhzeu1DilpnAXoiYZaXoOwE0WY4nT_zqGWBl8pEHQq4bp.ryc2AWVy3BhrYDnZZ2BlDnWpYXOc34Ata0UIbPcPJxnWrbiB9BoYgqpchaPYTzGlTiIqnJxvOB_O9MEJayWBNtNpLm2Q'
          ,"Referer": baseurl}
maxCount = 3
regVideo = re.compile(r"http(.*?)m3u8")
namereg = re.compile(r"(&#[0-9]*;)+")

class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url):
        # full_url = "%s/%s" % (baseurl.rstrip('/'), url.lstrip('/'))
        # fetcher = CurlFetcher()
        #
        # soup = fetcher.fetch(full_url)
        # return soup
        count = 0
        while count < maxCount:
            try:
                # 2. 修复后的 curl 命令（关键：补充终端环境变量、强制 IPv4、匹配终端特征）
                curl_command = [
                    'curl', baseurl+url,
                    '-H', 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    '-H', 'accept-language: zh-CN,zh;q=0.9',
                    '-H', 'cache-control: no-cache',
                    '-H', 'cookie: _ga=GA1.1.794066313.1759159626; __PPU_puid=7372220048289729256; UGVyc2lzdFN0b3JhZ2U=%7B%22CAIFRQ%22%3A%22ADXY8AAAAAAAAAABADR6XAAAAAAAAAAD%22%2C%22CAIFRT%22%3A%22ADXY8AAAAABo%252FvxQADR6XAAAAABo%252FvxQ%22%7D; bnState_1871751=%7B%22impressions%22%3A15%2C%22delayStarted%22%3A0%7D; hid=au4btf1fgsok0b8nfdo3ght3io; _ym_uid=1765987754368358150; _ym_d=1765987754; _ym_isad=2; _ym_visorc=b; _ga_ECF2QFGQ9G=GS2.1.s1765987754$o8$g1$t1765987755$j59$l0$h0; cf_clearance=HOEc0zDSi0IKxZ8bd3uS6_OGS17tS2VyrsLtdIomrzw-1765987756-1.2.1.1-cLQ3y.Pp2si17eYflg8XtnYAvGVc9Z7rmtiXR37dOCrOwrJU5N8ZJAXmUSaMYoUD.bo1opZ9UWiVULOLERxUs0Pzw94jhQbM5ARZ1OMf5tQRa22tphTdYucXQiUcl3FBXCoqce8IrgHIC1oxJY6IsYWIZNZBxa1lqWQQ7.tp3_.pRQ3OGCCGTDTXEtWCopLV2WWf42N96doI0fobZjLj7etwIEpAjIFK6lSd9JrNA5g',
                    '-H', 'pragma: no-cache',
                    '-H', 'priority: u=0, i',
                    '-H', 'sec-ch-ua: "Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
                    '-H', 'sec-ch-ua-arch: "arm"',
                    '-H', 'sec-ch-ua-bitness: "64"',
                    '-H', 'sec-ch-ua-full-version: "137.0.7151.120"',
                    '-H', 'sec-ch-ua-full-version-list: "Google Chrome";v="137.0.7151.120", "Chromium";v="137.0.7151.120", "Not/A)Brand";v="24.0.0.0"',
                    '-H', 'sec-ch-ua-mobile: ?0',
                    '-H', 'sec-ch-ua-model: ""',
                    '-H', 'sec-ch-ua-platform: "macOS"',
                    '-H', 'sec-ch-ua-platform-version: "14.3.0"',
                    '-H', 'sec-fetch-dest: document',
                    '-H', 'sec-fetch-mode: navigate',
                    '-H', 'sec-fetch-site: same-origin',
                    '-H', 'sec-fetch-user: ?1',
                    '-H', 'upgrade-insecure-requests: 1',
                    '-H', 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.7151.120 Safari/537.36',
                    '--compressed',
                ]
                process = subprocess.Popen(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                soup = BeautifulSoup(stdout)
                return soup

            except Exception as e:
                print("打开页面错误: %s" % common.format_exception(e) if 'common' in dir() else str(e))
                print("重试 %s，次数: %d" % (url, count))
                count += 1
                time.sleep(2)

        print("打开页面错误，重试%d次还是错误: %s" % (maxCount, url))
        return BeautifulSoup('')

    def header(self):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("hsex/header.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        print content
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist

    