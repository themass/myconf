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
from UrlFetcher import  UrlFetcher
reload(sys)
import subprocess
# 
sys.setdefaultencoding('utf8')

# 9226688.com 8182277.com 8283377.com qqav10.com qqav9.com qqav8.com qqav7.com qqav6.com qqav5.com 
baseurl = "https://t924.9p72p.com/"
header = {'User-Agent':
          'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html）Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)', 
          'Cookie':'CzG_fid21=1758821945; _ga=GA1.1.350018691.1758817990; CzG_sid=970t7K; utf8tt=26fcQWmwproJKgagzOxlq96xuT70iojHhiA%2BQ80L; CzG_fid33=1758822882; CzG_fid4=1758822442; CzG_oldtopics=D783537D783574D783517D783571D783451D781758D783555D783562D783582D783577D783587D; CzG_visitedfid=21D4D11D36D34D33; _ga_LTGT8CMVLT=GS2.1.s1758817990$o1$g1$t1758818913$j60$l0$h0; cf_clearance=brZ0We_5rG18oOz4ESqIr7bL68eAHdmHviHTkIgOE7E-1758818913-1.2.1.1-mJHYGIn7Z5kqIAzTHxBhhM2BbCD8XK99BRe7_ziT4hu48BeW6ns2QgNtTY3iZaPbsMSbHXnUWrI1f1yiE6.EeI5l41afGzqcuUgdB.p64b1UzJK5e9z5GkKL9ap8kUYVtqazWflsHl171mHBCwqw1wCRo7E29_IF2ZH7lZjYpFdlZ0R9adGKg7yQZ9VhBAlz6t13DJNreCoxm9c83HjP87ymcNDr25X2Y2cY0GQ4XtU'
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
                # # req = urllib2.Request(baseurl + url, headers=header)
                # # req.encoding = 'utf-8'
                # # response = urllib2.urlopen(req, timeout=3000)
                # # gzipped = response.headers.get(
                # #     'Content-Encoding')  # 查看是否服务器是否支持gzip
                # # content = response.read().decode('utf-8', errors='replace')
                # # if gzipped:
                # #     content = zlib.decompress(
                # #         content, 16 + zlib.MAX_WBITS)  # 解压缩，得到网页源码
                # # soup = BeautifulSoup(content)
                # # return soup
                #
                # curl_command = [
                #     'curl', url,
                #     '-H', 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                #     '-H', 'accept-language: zh-CN,zh;q=0.9',
                #     '-H', 'cache-control: no-cache',
                #     '-b', 'CzG_fid21=1758821945; _ga=GA1.1.350018691.1758817990; CzG_sid=970t7K; utf8tt=26fcQWmwproJKgagzOxlq96xuT70iojHhiA%2BQ80L; CzG_fid33=1758822882; CzG_fid4=1758822442; CzG_oldtopics=D783537D783574D783517D783571D783451D781758D783555D783562D783582D783577D783587D; CzG_visitedfid=21D4D11D36D34D33; _ga_LTGT8CMVLT=GS2.1.s1758817990$o1$g1$t1758818913$j60$l0$h0; cf_clearance=brZ0We_5rG18oOz4ESqIr7bL68eAHdmHviHTkIgOE7E-1758818913-1.2.1.1-mJHYGIn7Z5kqIAzTHxBhhM2BbCD8XK99BRe7_ziT4hu48BeW6ns2QgNtTY3iZaPbsMSbHXnUWrI1f1yiE6.EeI5l41afGzqcuUgdB.p64b1UzJK5e9z5GkKL9ap8kUYVtqazWflsHl171mHBCwqw1wCRo7E29_IF2ZH7lZjYpFdlZ0R9adGKg7yQZ9VhBAlz6t13DJNreCoxm9c83HjP87ymcNDr25X2Y2cY0GQ4XtU',
                #     '-H', 'pragma: no-cache',
                #     '-H', 'sec-ch-ua: "Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
                #     '-H', 'sec-ch-ua-mobile: ?0',
                #     '-H', 'sec-ch-ua-platform: "macOS"',
                #     '-H', 'sec-fetch-dest: document',
                #     '-H', 'sec-fetch-mode: navigate',
                #     '-H', 'sec-fetch-site: none',
                #     '-H', 'sec-fetch-user: ?1',
                #     '-H', 'upgrade-insecure-requests: 1',
                #     '-H', 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                #     '--compressed',
                #     '--insecure',
                #     '--verbose'
                # ]
                #
                # # 执行 curl 命令
                # process = subprocess.Popen(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # stdout, stderr = process.communicate()
                # # stdout = self.replace_by_regex(stdout)
                # print stdout
                # soup = BeautifulSoup(stdout)
                # return soup
                # ChromeDriver is currently pinned to an old major version on this
                # machine (for example, ChromeDriver 140 vs. Chrome 154/155).
                # Try curl first so a stale browser driver does not prevent normal
                # pages from being fetched.  Passing the cookie explicitly also
                # prevents UrlFetcher from trying to initialize Selenium just to
                # refresh cookies.
                fetcher = UrlFetcher()
                # The site uses index.php as the age-confirmation/session
                # entry point.  Visit it before requesting forum pages so the
                # curl cookie jar receives CzG_sid/utf8tt.
                fetcher.fetch_with_curl(baseurl + 'index.php', cookies='')
                page_content = fetcher.fetch_with_curl(url, cookies='')

                if (page_content and
                        not fetcher._is_cloudflare_challenge(page_content)):
                    return BeautifulSoup(page_content)

                # If the clean request is challenged, retry once with the
                # caller's existing cookies before considering Selenium.
                page_content = fetcher.fetch_with_curl(
                    url, cookies=header.get('Cookie'))
                if (page_content and
                        not fetcher._is_cloudflare_challenge(page_content)):
                    return BeautifulSoup(page_content)

                if page_content:
                    print 'curl 返回了 Cloudflare 验证页面，无法直接解析'

                # Selenium is an optional fallback.  Do not use the old hard-coded
                # /usr/local/bin/chromedriver path; set CHROMEDRIVER_PATH to a
                # driver whose major version matches the installed Chrome.
                chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')
                if chromedriver_path:
                    fetcher = UrlFetcher(chromedriver_path=chromedriver_path)
                    soup = fetcher.fetchUrl(url)
                    if soup and getattr(soup, 'contents', None):
                        return soup
                else:
                    print '未设置 CHROMEDRIVER_PATH，跳过 Selenium 回退'

                raise Exception('curl 未获取到可用页面')
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', (url if url.startswith('http') else baseurl + url), '次数', count
                count = count + 1
        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')
    # def replace_by_regex(self,text):
    #     pattern = re.compile(re.escape(start_str) + r'.*?' + re.escape(end_str), re.DOTALL)
    #     return pattern.sub('', text)
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
        with open("porn91luntan/header.html") as f:
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
        with open("porn91luntan/header2.html") as f:
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

    