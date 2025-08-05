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
import ssl
import socket
import subprocess

reload(sys)
# 
sys.setdefaultencoding('utf8')

# 9226688.com 8182277.com 8283377.com qqav10.com qqav9.com qqav8.com qqav7.com qqav6.com qqav5.com 
baseurl = "https://avhd101.com"
headers = {'User-Agent':
               'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html）Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
           'Cookie':'Hm_lvt_a7dbcd0d5fd2dbdc43e5060c94acaa09=1527844837; PHPSESSID=g8ueibtojgjuub262ae109m2j1; Hm_lvt_c0060128b5e4b5b38a10be83f06960fd=1530951178; msvod_from_url=CXHdyI37jSHtNtnU%2FGBkOiMfjYp75b9bAMxJauXJEbCph8pO90GzNwM; msvod_user_id=sTLyUSP2KKex0l%2FenE0; msvod_user_login=0BUv%2FRmatXLtwy8ku6E2s8cfhsoQfkASdur2QcWy8wZb0twm3WRbkA; msvod_pl_token=A_FO9jJ79ZZkyVFTBxw1KLmX; Hm_lpvt_c0060128b5e4b5b38a10be83f06960fd=1530951284; msvod_token=_pF0%2FpHf%2FPEKXfOFQGGwSyOE'
    ,"Referer": baseurl}
maxCount = 3
regVideo = re.compile(r'http(.*?)m3u8"')
namereg = re.compile(r"(&#[0-9]*;)+")
video_url = "https://m3u8.44cdn.com"
class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.baseurl = baseurl
        # 模拟浏览器 headers，减少被拒绝概率
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }
        self.max_retries = maxCount
        # 自定义SSL上下文（进一步放宽限制）
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
        # 允许较旧的SSL/TLS协议（应对服务器协议兼容问题）
        self.ctx.options |= ssl.OP_NO_SSLv2
        self.ctx.options |= ssl.OP_NO_SSLv3
        # 可选：根据服务器支持的协议调整（如允许TLSv1.0/1.1）
        # self.ctx.options &= ~ssl.OP_NO_TLSv1
        # self.ctx.options &= ~ssl.OP_NO_TLSv1_1
        self._init_ssl_context()
    def _init_ssl_context(self):
        """初始化SSL上下文，支持更多协议和选项"""
        # 创建不验证证书的上下文
        self.ssl_ctx = ssl.create_default_context()
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.verify_mode = ssl.CERT_NONE

        # 启用TLSv1.0和TLSv1.1（兼容旧服务器）
        self.ssl_ctx.options &= ~ssl.OP_NO_TLSv1
        self.ssl_ctx.options &= ~ssl.OP_NO_TLSv1_1

        # 禁用压缩（避免CRIME攻击相关问题）
        self.ssl_ctx.options |= ssl.OP_NO_COMPRESSION

        # 移除不兼容的属性设置
        # self.ssl_ctx.session_cache_mode = ssl.SESSION_CACHE_OFF  # Python 2.7不支持

    def fetchUrl(self, url):
        count = 0
        while count < maxCount:
            try:
                # req = urllib2.Request(baseurl + url, headers=header)
                # req.encoding = 'utf-8'
                # response = urllib2.urlopen(req, timeout=3000)
                # gzipped = response.headers.get(
                #     'Content-Encoding')  # 查看是否服务器是否支持gzip
                # content = response.read().decode('utf-8', errors='replace')
                # if gzipped:
                #     content = zlib.decompress(
                #         content, 16 + zlib.MAX_WBITS)  # 解压缩，得到网页源码
                # soup = BeautifulSoup(content)
                # return soup

                curl_command = [
                    'curl', baseurl+url,
                    '-H', 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    '-H', 'accept-language: zh-CN,zh;q=0.9',
                    '-H', 'cache-control: no-cache',
                    '-H', 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    '-H', 'accept-language: zh-CN,zh;q=0.9',
                    '-H', 'cache-control: no-cache',
                    '-H', 'pragma: no-cache',
                    '-H', 'priority: u=0, i',
                    '-H', 'referer: https://avhd101.com/search?q=%E6%BD%AE%E5%90%B9',
                    '-H', 'sec-ch-ua: "Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
                    '-H', 'sec-ch-ua-mobile: ?0',
                    '-H', 'sec-ch-ua-platform: "macOS"',
                    '-H', 'sec-fetch-dest: document',
                    '-H', 'sec-fetch-mode: navigate',
                    '-H', 'sec-fetch-site: same-origin',
                    '-H', 'sec-fetch-user: ?1',
                    '-H', 'upgrade-insecure-requests: 1',
                    '-H', 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                    '-b', 'rr=direct; iadult=1; hello=1; _gid=GA1.2.869876431.1754095822; '
                          'CloudFront-Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wdi5hdmhkMTAxLmNvbS8qIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzU0MTAzMDI2fX19XX0_; '
                          'CloudFront-Signature=NNZ4jBCPXjPT~jh1-UqwjoePDAIIY2yqvOVlJkpRs~28DipwkHNAlmawPu2FYHsQ~dlqrcd86ESLXvNK3ZNPdck0Yzp0K38DcFrX4r3fsHb1GDDDmoZCetiEKeEf~qAdmeZFqcMPPFuFcuaieZaHeu88X-yKrRCOapV8WsyB2ef36Wt4~2sKjZmtb672ADF1gzAHFTMsaNyS08rRQq7YwxzRSXaeLLrmKZdQR2Jc~txBtlIpQzoY-Bsh1cGdjb1UTJMJB1g3oHd7DnnDyjc3HoQqde9dDE3PjOUWue3nIYWT0fM3Z7SoXTPFgJ3qnKap673WFGDdMjUB9ww5Prsd~g__; '
                          'CloudFront-Key-Pair-Id=APKAILCKQMWBGAX3WDAQ; _gat_gtag_UA_78207029_1=1; '
                          'cf_clearance=5SgAgo6mvLn4Xkmw15dVQVGzJ_jQw9IXAIiMzC68DDI-1754098078-1.2.1.1-Q9vjYg6NW5kyTEoSeEbQykZCWNcxmJj.ZzH2R8Eox_XngWsW_yJGjbPO0w.lukX2PuZSOX2iuDvn2gB_tPnXn61VnSdqt3qOpoQxoxtmNSMOBoTOVek39733o.pVS__IZU9BURuhu293sT.gKYEGqnfWzsagZzY9Aer9nOc1T6Sdz6mGRMW3kLSesjkZkIe8.GJVuCgfFvUSbiilJHgO5FH355NFtsnmf9jO_gleZZc; '
                          'XSRF-TOKEN=eyJpdiI6InRsakRiWjRmM2N3dktxMFJ6NmpWdHc9PSIsInZhbHVlIjoiMDBjeTNxXC83ZkpzWE1YcitsQ1NIalM1SlMrMEdOZ0xTTEROTDZpb1FYVEhMZFRkUTZ6YTArbEowbTdpTHRtSHMiLCJtYWMiOiJmNzBjMjU4MzljMzAzNjBlOTc0OGY1MWM1MGQ0YjdiYzFiMWUzYTY0ZjFhMzNlOWU3MDkyYWE5OGZkYjBmMGUyIn0%3D; '
                          'miao_ss=eyJpdiI6Ik4rdUhYalYrcDh1R1BPOXlURDlPUlE9PSIsInZhbHVlIjoiNUplemlHOFllY2c3YTJsZENORUZEUm5iOUdGQkNxQllaY0RpRysyN2M0OWwzWnhKSzhZT0dsVHFzUWcyblBDQSIsIm1hYyI6ImJhNmM4NTY0YWFiM2UzYmM3OGZjZTg3OTA5YTExOTEwN2ZiMDA0NjA0YWI0NWM4NGM5OWE5MzE4YTAxMGEyZDUifQ%3D%3D; '
                          '_ga_TZVQ25ZKTH=GS2.1.s1754095821$o1$g1$t1754098103$j30$l0$h0; _ga=GA1.2.1697842212.1754095822'                    '-H', 'pragma: no-cache',
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
    def fetchUrlContent(self, url):
        max_retries = 5
        for attempt in xrange(max_retries):
            try:
                # 创建请求对象
                req = urllib2.Request(baseurl+url, headers=self.headers)

                # 设置超时并打开URL
                socket.setdefaulttimeout(30)
                response = urllib2.urlopen(req, timeout=30, context=self.ssl_ctx)

                # 获取响应内容
                content_encoding = response.headers.getheader('Content-Encoding', '')
                content = response.read()

                # 处理gzip压缩内容
                if 'gzip' in content_encoding.lower():
                    content = zlib.decompress(content, 16 + zlib.MAX_WBITS)
                return content

            except ssl.SSLError as e:
                print "SSL错误 ({0}/{1}): {2} - {3}".format(
                    attempt+1, max_retries, url, str(e))

                # 针对特定错误尝试不同的SSL上下文
                if 'KRB5_S_TKT_NYV' in str(e) or 'unexpected eof' in str(e).lower():
                    # 尝试更宽松的上下文
                    self.ssl_ctx = ssl._create_unverified_context()

            except (urllib2.URLError, socket.timeout) as e:
                print "网络错误 ({0}/{1}): {2} - {3}".format(
                    attempt+1, max_retries, url, str(e))

            except Exception as e:
                print "其他错误 ({0}/{1}): {2} - {3}".format(
                    attempt+1, max_retries, url, str(e))

            # 指数退避重试
            wait_time = 2 ** attempt
            print "等待 {0} 秒后重试...".format(wait_time)
        print "达到最大重试次数，无法获取: {0}".format(url)
        return None

    def fetchUrlWithBase(self, url):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(url, headers=headers)
                content = urllib2.urlopen(req, timeout=300).read()
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', url, '次数', count
                count = count + 1
        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')
    def header(self):
        #         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__))
        with open("avhd/header.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def header2(self):
        #         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__))
        with open("avhd/header2.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def headerImg(self):
        #         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__))
        with open("jiu667/header2.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
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

        print '打开页面错误,重试3次还是错误', url
        return ''

    