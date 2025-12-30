#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import zlib
import urllib2
import threading
from common.envmod import *
from common import db_ops
from common import httputil
from common import common
import threading,os
from BeautifulSoup import BeautifulSoup
import re,sys
import time
reload(sys)
# 
sys.setdefaultencoding('utf8')
import subprocess
import requests
start_str = "x-cloak"
end_str = 'class="lozad w-full"'
# 9226688.com 8182277.com 8283377.com qqav10.com qqav9.com qqav8.com qqav7.com qqav6.com qqav5.com 
baseurl = "https://missav.ai/"
header = {
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
maxCount = 3
regVideo = re.compile(r"http(.*?)m3u8")
namereg = re.compile(r"(&#[0-9]*;)+")

class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
    def fetchUrlWithBase(self, url):
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
                    'curl', url,
                    '-H', 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    '-H', 'accept-language: zh-CN,zh;q=0.9',
                    '-H', 'cache-control: no-cache',
                    '-b', 'user_uuid=a038d380-a8c0-4805-b56e-eabc06658799; _ga=GA1.1.963000055.1745343337; search_history=[%22spa%22]; _ga_0C6GHNFYBF=GS2.1.s1758816111$o10$g0$t1758816294$j52$l0$h0; cf_clearance=6NzhA3j3ChJcauV1M8GrEol36SoCujuF0NOVjZq23q4-1761839546-1.2.1.1-c.oFHN6s1aWM0poXhggSW5pirH5jFpxxROPVvNGui8PHdpEeZE.8.ysQBnJrPo31ahrFy0JfoY2vecpmc6Ce.JKdXuBwt.wrLJCpaeGUE6BkE9_XAA_VRDhrMjDrkvvO8_54diL_Qfp_KYm.CfkInCz58T22XAKftnneq9Ykg1Wi5nEtbO0aD0M0HPUDOYx3BxxG4J3ImAZdFbaaV1PgFqkHqodo2ovVm6dSx3X6ceQ; _ga_WVQPWV98M1=GS2.1.s1761839547$o1$g0$t1761839547$j60$l0$h0',
                    '-H', 'pragma: no-cache',
                    '-H', 'sec-ch-ua: "Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
                    '-H', 'sec-ch-ua-mobile: ?0',
                    '-H', 'sec-ch-ua-platform: "macOS"',
                    '-H', 'sec-fetch-dest: document',
                    '-H', 'sec-fetch-mode: navigate',
                    '-H', 'sec-fetch-site: none',
                    '-H', 'sec-fetch-user: ?1',
                    '-H', 'upgrade-insecure-requests: 1',
                    '-H', 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                    '--compressed',
                    '--insecure',
                    '--verbose'
                ]

                # 执行 curl 命令
                process = subprocess.Popen(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                stdout = self.replace_by_regex(stdout)
                soup = BeautifulSoup(stdout)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', baseurl + url, '次数', count
                count = count + 1
                time.sleep(1)

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')
    def replace_by_regex(self,text):
        pattern = re.compile(re.escape(start_str) + r'.*?' + re.escape(end_str), re.DOTALL)
        return pattern.sub('', text)
    def fetchUrlWithBaseText(self, url):
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
                    'curl', url,
                    '-H', 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    '-H', 'accept-language: zh-CN,zh;q=0.9',
                    '-H', 'cache-control: no-cache',
                    '-b', 'user_uuid=a038d380-a8c0-4805-b56e-eabc06658799; _ga=GA1.1.963000055.1745343337; cf_clearance=QnSAwkngk4W5exaWWCR7JXTJBGFPK7ApdtPkJHlnaBE-1749880763-1.2.1.1-09aU2TOm8sOotWwJ4dkAfS5927mXRC646b7cdOFlLZdmaFKkH9vlykNio7Pj.XrKCrtkF8ZB.zWCyKYTAPm97JG7w2ZsifEB8bE24eWlxL6LoKuevi4vFhaVR14edcYOHxp7rweUS8z7P9hhQj262CfpOokPyFzotDBW7NVSExKnPdp3Oa6i.4GHVtjwCA7W3wVy8B4It0RG1QNdlWtOjBvI6mPYs.Y1DV1o7sMn3F3lKZezofjzSL7j3SWRk0wzckI0o6ikHpI6FAkOcyGTHu7Duxsjm1JcGf3APh1ibaGIvQxlS7IDF56hTEex0rZSbyJTAy72XHx2PxhQb8kja50ey29q6L17Htu5jSGy1Ac; _ga_0C6GHNFYBF=GS2.1.s1751801059$o7$g0$t1751801059$j60$l0$h0',
                    '-H', 'pragma: no-cache',
                    '-H', 'sec-ch-ua: "Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
                    '-H', 'sec-ch-ua-mobile: ?0',
                    '-H', 'sec-ch-ua-platform: "macOS"',
                    '-H', 'sec-fetch-dest: document',
                    '-H', 'sec-fetch-mode: navigate',
                    '-H', 'sec-fetch-site: none',
                    '-H', 'sec-fetch-user: ?1',
                    '-H', 'upgrade-insecure-requests: 1',
                    '-H', 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                    '--compressed',
                    '--insecure',
                    '--verbose'
                ]
                # 执行 curl 命令
                process = subprocess.Popen(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                return stdout
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', baseurl + url, '次数', count
                count = count + 1
                time.sleep(1)

        print '打开页面错误,重试3次还是错误', url
        return ''
    # def fetchUrl(self, url):
    #     count = 0
    #     while count < maxCount:
    #         try:
    #             req = urllib2.Request(url, headers=header)
    #             req.encoding = 'utf-8'
    #             response = urllib2.urlopen(req, timeout=3000)
    #             gzipped = response.headers.get(
    #                 'Content-Encoding')  # 查看是否服务器是否支持gzip
    #             content = response.read().decode('utf-8', errors='replace')
    #             if gzipped:
    #                 content = zlib.decompress(
    #                     content, 16 + zlib.MAX_WBITS)  # 解压缩，得到网页源码
    #             soup = BeautifulSoup(content)
    #             return soup
    #         except Exception as e:
    #             print common.format_exception(e)
    #             print '打开页面错误,重试',  url, '次数', count
    #             count = count + 1
    #             time.sleep(1)
    #
    #     print '打开页面错误,重试3次还是错误', url
    #     return BeautifulSoup('')

    # def fetchUrlWithBase(self, url):
    #     count = 0
    #     while count < maxCount:
    #         try:
    #             # req = urllib2.Request(url, headers=header)
    #             # print req.headers
    #             # content = urllib2.urlopen(req, timeout=300).read()
    #             content = httputil.getText(url = url, header = header, isGzip=True)
    #             pattern = r'x-cloak\s+:class="{ hidden: showPreview === \'[a-zA-Z0-9\-]+\' \|\| holdPrevieai\.includes\(\'[a-zA-Z0-9\-]+\'\) }"'
    #             new_text = re.sub(pattern, '', content)
    #             soup = BeautifulSoup(new_text)
    #             return soup
    #         except Exception as e:
    #             print common.format_exception(e)
    #             print '打开页面错误,重试', url, '次数', count
    #             count = count + 1
    #             time.sleep(1)
    #
    #     print '打开页面错误,重试3次还是错误', url
    #     return BeautifulSoup('')
    def header(self,name):
#         content = self.fetchContentUrl(headerUrl, header)
        content=''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)) 
        with open("%s%s"%("missav/",name)) as f:
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

    