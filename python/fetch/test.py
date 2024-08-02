#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
import threading
from BeautifulSoup import BeautifulSoup
import sys

import common.httputil

reload(sys)
sys.setdefaultencoding('utf8')
import subprocess
import requests
from common import *
def fetchUrl(url):
#     req = urllib2.Request(url, headers={
#                 'User-Agent': 'Mozilla/5.0 (Linux; U; Android 8.0.0; zh-cn; HWI-AL00 Build/HUAWEIHWI-AL00) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30', "Referer":url
#                 ,"Host": "yepu.swapdox.com","Accept-Encoding": "gzip",
#                 "T-Token": "sPl1gaqimReMELUvMQ4s8w==","X-ONEX-AUTH":"" })
# #     req.encoding = 'utf-8'
#     response = urllib2.urlopen(req, timeout=3000)
#     gzipped = response.headers.get(
#         'Content-Encoding')  # 查看是否服务器是否支持gzip
#     content = response.read().decode('utf8', errors='replace').replace("<![endif]-->","")
#     return  BeautifulSoup(content)

    command = '''
    curl 'https://missav.com/dm265/cn/chinese-subtitle?page=1' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'cache-control: no-cache' \
  -H 'cookie: user_uuid=07ca7f21-0a08-42ff-b963-8236cd0e82e2; _ga=GA1.1.600459745.1722393954; dom3ic8zudi28v8lr6fgphwffqoz0j6c=694fe64e-46e5-4b9b-bfdc-6c8ea530e9e7%3A2%3A1; sb_main_62bdca270715b3b43fbac98597c038f1=1; sb_count_62bdca270715b3b43fbac98597c038f1=6; sb_onpage_62bdca270715b3b43fbac98597c038f1=0; sb_page_62bdca270715b3b43fbac98597c038f1=21; _ga_Z3V6T9VBM6=GS1.1.1722532041.5.0.1722532041.0.0.0; cf_clearance=W2kbJdLi8pCJ29RC9w4hgjsxGr4H81eRPFAr75dqQec-1722532043-1.0.1.1-sfQGKHLA.CaN8RipoZkFfVQZ_V.LckWvlRtXxLLnfttEME1fkp9fbkghQkaHBka.65wTK1wC9249pYmWx00Cyg' \
  -H 'pragma: no-cache' \
  -H 'priority: u=0, i' \
  -H 'sec-ch-ua: "Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: document' \
  -H 'sec-fetch-mode: navigate' \
  -H 'sec-fetch-site: none' \
  -H 'sec-fetch-user: ?1' \
  -H 'upgrade-insecure-requests: 1' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    '''
    # process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    # output, error = process.communicate()
    #
    # if error:
    #     print "Error: \n", error
    #
    # print output

    url = 'https://missav.com/dm504/cn/release?page=1'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'cookie': 'user_uuid=07ca7f21-0a08-42ff-b963-8236cd0e82e2; _ga=GA1.1.600459745.1722393954; dom3ic8zudi28v8lr6fgphwffqoz0j6c=694fe64e-46e5-4b9b-bfdc-6c8ea530e9e7%3A2%3A1; sb_main_62bdca270715b3b43fbac98597c038f1=1; sb_count_62bdca270715b3b43fbac98597c038f1=6; sb_onpage_62bdca270715b3b43fbac98597c038f1=0; sb_page_62bdca270715b3b43fbac98597c038f1=21; _ga_Z3V6T9VBM6=GS1.1.1722532041.5.0.1722532041.0.0.0; cf_clearance=W2kbJdLi8pCJ29RC9w4hgjsxGr4H81eRPFAr75dqQec-1722532043-1.0.1.1-sfQGKHLA.CaN8RipoZkFfVQZ_V.LckWvlRtXxLLnfttEME1fkp9fbkghQkaHBka.65wTK1wC9249pYmWx00Cyg',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    data = httputil.getText(url = url, header = headers, isGzip=True)
    print data
    # response = requests.get(url, headers=headers)
    # print response.text

if __name__ == '__main__':
    fetchUrl("")