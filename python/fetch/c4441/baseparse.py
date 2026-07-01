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
reload(sys)
# 
sys.setdefaultencoding('utf8')

# https://www.9k88x.com
baseurl = "https://t92ts2.com"
headers = {'User-Agent':
               'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html）Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
           'Cookie':'Hm_lvt_95e2aff1f817e78b047d2bd592dab054=1780067916; HMACCOUNT=5435569E4E0FEDC7; Hm_lpvt_95e2aff1f817e78b047d2bd592dab054=1780067944; dialog_closed=true; second_dialog_closed=true'
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
        """带重试机制的页面抓取方法"""
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
                return BeautifulSoup(content)

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
        return ""
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
        with open("c4441/header.html") as f:
            for line in f.readlines():
                content = "%s%s"%(content,line)
        soup= BeautifulSoup(content)
        alist = soup.findAll('a')
        return alist
    def header2(self):
        #         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__))
        with open("c4441/header2.html") as f:
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

    