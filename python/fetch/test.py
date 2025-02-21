#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
import threading
from BeautifulSoup import BeautifulSoup
import sys

import common.httputil
import re

reload(sys)
sys.setdefaultencoding('utf8')
import subprocess

import requests
from common import *
import subprocess

curl_command = [
    'curl', 'https://missav.ws/dm549/cn/release',
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
# process = subprocess.Popen(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# stdout, stderr = process.communicate()
#
# # 打印输出和错误信息
# print(stdout)
# soup = BeautifulSoup(stdout)
# print soup.first("div",{"class":"py-1"})
# if stderr:
#     print("Error:", stderr)
response = requests.get("https://missav.ws/dm549/cn/release", timeout=30, verify=False)  # 跳过证书验证
print response.text