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
reload(sys)
# 
sys.setdefaultencoding('utf8')

# 9226688.com 8182277.com 8283377.com qqav10.com qqav9.com qqav8.com qqav7.com qqav6.com qqav5.com 
baseurl = "https://missav.com/"
header = {'User-Agent':
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
          'Cookie':'user_uuid=07ca7f21-0a08-42ff-b963-8236cd0e82e2; _ga=GA1.1.600459745.1722393954; cf_clearance=e9BqL9LQZHRlngCxmOtMXdxs6YQgIHE0NyC0CYtIiFw-1722446371-1.0.1.1-NYR3NRfal7dj9cbP6f_5334MQ1XyWK4UWS4_ngf3i_GSEyLWYJoM_k6.L68Uw8IdgPwfYXOSoBWPFz1fX9a0rw; dom3ic8zudi28v8lr6fgphwffqoz0j6c=694fe64e-46e5-4b9b-bfdc-6c8ea530e9e7%3A2%3A1; sb_main_62bdca270715b3b43fbac98597c038f1=1; sb_count_62bdca270715b3b43fbac98597c038f1=6; sb_onpage_62bdca270715b3b43fbac98597c038f1=0; XSRF-TOKEN=eyJpdiI6IjNDSUtPU1ZWREEwM3IzVlZGdG5oZ3c9PSIsInZhbHVlIjoiOVV6RmpTcnpHaDc5TVg2dmN4UUxBaE1PbWdwS1FQOWdQMnNKNkEvNkJ6OUdXRml2UkY2Mkp0MmwvM2ZYSU0wWnd5aHhpNDRreEZDS2dEZTk5cGllUWYxS1ZINTl5Uk1KYkwxRnhqRk5hYkNOWjRhRW5WV2xLZnhUZms3cVhjN3giLCJtYWMiOiI4OWZkMGFiY2RlZDc2MGMxZGFjZGJmNGRmN2U5NWIxYTczZWI1NDM2NzNiY2RhM2NhMTJiMmQwMjc1OThlNjgzIiwidGFnIjoiIn0%3D; missav_session=eyJpdiI6IkNsOWg4Z29yTTBQUVhmaFFYNm9yZUE9PSIsInZhbHVlIjoiUWQ3L1FDTWRHVUVSMmowL1FSK1lXYS9GeWdKb09hZFJNbktYR21JWHYzanVDVktJK2U0Vk1tencwV0tnNjlQVStXZWNZTUlIbzdxVUxyRTcvUTRGT3B4SkdXN1FFRXN5dWNSV24zZXRQMWo4STYxVUp3Z1dqMzFmTU01c284dVYiLCJtYWMiOiI1OGVkYThmN2UyOTZlYTgxYjA0MWEwNzI3MTVhMGQwNjQwMDNlMjY1OGM4YjVmODU4OTUyYTZkZjYyNmI2NDIzIiwidGFnIjoiIn0%3D; capfrMu0V6qRsn6rSi6pdY5SFUzwjgYmk3rDOUbw=eyJpdiI6InhCQ1UwbG1LRVROYXAvd3lBMHU5TUE9PSIsInZhbHVlIjoiVXRFTGY5cVQrc21sSC9CYUR6dHdsSWd1aEdkUGtWdWZidTB2enhXZFNwQlJKczQwYkIyNnZRVjliQmIwa1RMbktRTFVIdXdDSFprOVBGcG9EaWo4ZXhoZTFaZlRUcmYwOTdoK0NIQzdGV0oyckNiY1ROalVYZ1dyMzdOMVUrcVhxeE45WVFOaFVoT25VMEFRNGJXMS95L2tpT1c2b2RsSDQrS3ZncWx0YVNwODFCWFNrcCtDanYvbDdkbVVIWFJVUE1XTlZvaytzQTdlSnQvSnRaa3Vxa2xaeFIrNzJMaGJ0WFRpbWVwelF0Nkc4ZnhoMnNWSnJNZFVoakY0U3NTTFlSTjNkdTZzZzdmZzg0dXlrSlJEZGh4OUNxTXpCS2VDZUtRMTdYd0VWNWIyWGFXQmFQZ0pNRXU2U3FYS29ReFM1UTF5dGY5UlVTZVJNRmx4OVZVdUQ3RW9hOHZoamhLQnNsNStIakgyVGlYd01udTFpUUFnb05zTGllRCtycDJ1RkpzK1RRdWZJWVR6cjBSejU5Z25Qdz09IiwibWFjIjoiZmE5ZTQxOWRkYTM0OTBiZWVmNmM5YTA3YzJjMTQ1YzY1NTMwZjM3OTNjYzNhNWI1MjA0NWEwMGUwNTgyMDRlMCIsInRhZyI6IiJ9; sb_page_62bdca270715b3b43fbac98597c038f1=21; _ga_Z3V6T9VBM6=GS1.1.1722446370.3.1.1722448027.0.0.0'
          ,"Referer": baseurl}
maxCount = 3
regVideo = re.compile(r"http(.*?)m3u8")
namereg = re.compile(r"(&#[0-9]*;)+")

class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl + url, headers=header)
                req.encoding = 'utf-8'
                response = urllib2.urlopen(req, timeout=3000)
                gzipped = response.headers.get(
                    'Content-Encoding')  # 查看是否服务器是否支持gzip
                content = response.read().decode('utf-8', errors='replace')
                if gzipped:
                    content = zlib.decompress(
                        content, 16 + zlib.MAX_WBITS)  # 解压缩，得到网页源码
                soup = BeautifulSoup(content)
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
        with open("missav/header.html") as f:
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

    