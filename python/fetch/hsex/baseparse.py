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
        full_url = "%s/%s" % (baseurl.rstrip('/'), url.lstrip('/'))
        fetcher = CurlFetcher()

        soup = fetcher.fetch(full_url)
        return soup
        # count = 0
        # full_url = "%s/%s" % (baseurl.rstrip('/'), url.lstrip('/'))
        # while count < maxCount:
        #     try:
        #         # req = urllib2.Request(baseurl + url, headers=header)
        #         # req.encoding = 'utf-8'
        #         # response = urllib2.urlopen(req, timeout=3000)
        #         # gzipped = response.headers.get(
        #         #     'Content-Encoding')  # 查看是否服务器是否支持gzip
        #         # content = response.read().decode('utf-8', errors='replace')
        #         # if gzipped:
        #         #     content = zlib.decompress(
        #         #         content, 16 + zlib.MAX_WBITS)  # 解压缩，得到网页源码
        #         # soup = BeautifulSoup(content)
        #         # return soup
        #
        #         # 2. 修复后的 curl 命令（关键：补充终端环境变量、强制 IPv4、匹配终端特征）
        #         curl_command = [
        #             'curl', full_url,
        #             # 核心修复1：强制使用 IPv4（终端默认可能用 IPv4，Python 可能用 IPv6，导致 IP 特征不一致）
        #             '-4',
        #             # 核心修复2：传递终端的环境变量（模拟终端执行环境）
        #             '-H', 'X-Environment: terminal',  # 自定义头标识，非必需但可增强一致性
        #             # 原始请求头（与终端 curl 完全一致）
        #             '-H', 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        #             '-H', 'accept-language: zh-CN,zh;q=0.9',
        #             '-H', 'cache-control: no-cache',
        #             # Cookie（与终端 curl 完全一致，注意：若过期需从终端重新复制）
        #             '-H', 'cookie: _ga=GA1.1.562282098.1743184592; __PPU_puid=7372220048289729256; hid=fqon093adrbeju7n89qe4hlh8k; cf_clearance=JPNDVBtt9SP2ZxFId1rpzzrGImkoZpFNN5w9TsgpDwM-1759071414-1.2.1.1-5bqwhuiELPe3aAV1PRRv.vpGYzqefTacI0d44jHqhYKCM4MnTf60h7pWAodwOWs7OPYIMCRWZjZbfDOKV3L9vrVPNm.PA.GRsgGB9EAE.0O.KXpUh56K3bWwROa3k60aYeVk1h8A7DvurqsoFKgBUlKe.POgjnQLcQDwCEcQTsx5kQiTB_k5VhW0N8QAjZmojA3bRJK7YiQA2Smfz_Ly8UZ7ybRWD5PMW4gZhC8wDbpKJ7GZ9fFrmXoMKw1DKY5X; _ga_ECF2QFGQ9G=GS2.1.s1759071414$o6$g1$t1759071464$j10$l0$h0; UGVyc2lzdFN0b3JhZ2U=%7B%22CAIFRQ%22%3A%22ADXY8AAAAAAAAAABADR6ZgAAAAAAAAABADR6XAAAAAAAAAAB%22%2C%22CAIFRT%22%3A%22ADXY8AAAAABo2hJQADR6ZgAAAABo2hJQADR6XAAAAABo2hJQ%22%7D; bnState_1871751={"impressions":7,"delayStarted":0}',
        #             '-H', 'pragma: no-cache',
        #             '-H', 'priority: u=0, i',
        #             '-H', 'sec-ch-ua: "Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        #             '-H', 'sec-ch-ua-arch: "arm"',
        #             '-H', 'sec-ch-ua-bitness: "64"',
        #             '-H', 'sec-ch-ua-full-version: "137.0.7151.120"',
        #             '-H', 'sec-ch-ua-full-version-list: "Google Chrome";v="137.0.7151.120", "Chromium";v="137.0.7151.120", "Not/A)Brand";v="24.0.0.0"',
        #             '-H', 'sec-ch-ua-mobile: ?0',
        #             '-H', 'sec-ch-ua-model: ""',
        #             '-H', 'sec-ch-ua-platform: "macOS"',
        #             '-H', 'sec-ch-ua-platform-version: "14.3.0"',
        #             '-H', 'sec-fetch-dest: document',
        #             '-H', 'sec-fetch-mode: navigate',
        #             '-H', 'sec-fetch-site: same-origin',
        #             '-H', 'sec-fetch-user: ?1',
        #             '-H', 'upgrade-insecure-requests: 1',
        #             # 核心修复3：User-Agent 与终端 curl 完全一致（原代码中 Chrome 版本是 137.0.0.0，终端是 137.0.7151.120，存在细微差异）
        #             '-H', 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.7151.120 Safari/537.36',
        #             # 保留压缩和 SSL 跳过（与终端一致）
        #             '--compressed',
        #             '--insecure',
        #             # 核心修复4：强制 curl 使用终端的 DNS 解析（避免 Python 环境 DNS 差异）
        #             '--resolve', '%s:443:104.21.xx.xx' % baseurl.lstrip('https://'),  # 替换为终端 ping 出的 IP
        #             # 核心修复5：模拟终端的连接超时和响应超时（避免默认超时差异）
        #             '--connect-timeout', '10',
        #             '--max-time', '30'
        #         ]
        #
        #         # 3. 执行 curl 命令（关键：传递终端的环境变量，如 PATH、USER 等）
        #         # 获取终端环境变量（排除 Python 新增的干扰变量）
        #         terminal_env = os.environ.copy()
        #         # 保留关键环境变量，移除可能暴露 Python 的变量
        #         keep_env = ['PATH', 'USER', 'HOME', 'LC_ALL', 'LANG', 'TERM']
        #         clean_env = {k: v for k, v in terminal_env.items() if k in keep_env}
        #
        #         # 启动 subprocess 时传入终端环境变量
        #         process = subprocess.Popen(
        #             curl_command,
        #             stdout=subprocess.PIPE,
        #             stderr=subprocess.PIPE,
        #             env=clean_env,  # 核心：用终端环境执行 curl
        #             shell=False  # 禁用 shell，避免环境变量注入（更安全）
        #         )
        #
        #         # 4. Python 2.7 超时处理（与终端 curl 超时一致）
        #         def timeout_handler(signum, frame):
        #             raise Exception("curl 请求超时（30秒）")
        #
        #         signal.signal(signal.SIGALRM, timeout_handler)
        #         signal.alarm(30)  # 与 --max-time 一致
        #
        #         # 获取输出
        #         stdout, stderr = process.communicate()
        #         signal.alarm(0)  # 取消超时
        #
        #         # 5. 检查 curl 执行状态（终端执行成功的关键：returncode 必须为 0）
        #         if process.returncode != 0:
        #             print("curl 执行失败（代码: %d），终端错误信息: %s" % (process.returncode, stderr))
        #             count += 1
        #             time.sleep(2)
        #             continue
        #
        #         # 6. 检测是否被 Cloudflare 拦截（避免返回验证页面）
        #         stdout_str = stdout.decode('utf-8', errors='replace')
        #         if "cloudflare" in stdout_str.lower() or "just a moment" in stdout_str.lower():
        #             print("警告：被 Cloudflare 拦截，尝试刷新 Cookie...")
        #             # 提示：此时需从终端重新复制最新的 cf_clearance（Cookie 可能已过期）
        #             count += 1
        #             time.sleep(5)
        #             continue
        #
        #         # 7. 解析页面并返回（显式指定编码，避免乱码）
        #         soup = BeautifulSoup(stdout_str, "html.parser", from_encoding="utf-8")
        #         print("成功获取页面，标题: %s" % (soup.title.text if soup.title else "无标题"))
        #         return soup
        #
        #     except Exception as e:
        #         print("打开页面错误: %s" % common.format_exception(e) if 'common' in dir() else str(e))
        #         print("重试 %s，次数: %d" % (full_url, count))
        #         count += 1
        #         time.sleep(2)
        #
        # print("打开页面错误，重试%d次还是错误: %s" % (maxCount, full_url))
        # return BeautifulSoup('')

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

    