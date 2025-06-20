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
                    '-H', 'cookie: _ga=GA1.1.611983894.1716478735; __PPU_puid=7372220048289729256; UGVyc2lzdFN0b3JhZ2U=%7B%22CAIFRQ%22%3A%22ACZSQQAAAAAAAAAB%22%2C%22CAIFRT%22%3A%22ACZSQQAAAABncNdQ%22%2C%22MTIFRQ%22%3A%22ADO5uwAAAAAAAAAB%22%2C%22MTIFRT%22%3A%22ADO5uwAAAABncNdQ%22%7D; bnState_1871751={"impressions":1,"delayStarted":0}; hid=b3ac650730881e9e1d5c5e073b89d300; _ga_ECF2QFGQ9G=GS1.1.1735994610.15.0.1735994610.0.0.0; cf_clearance=qskGiffzDuD6YFS3fYw6VdzsMo62HfZLvHUd8vCa3yw-1735994615-1.2.1.1-i8ytuvtyOniXQwBOHj1sTCEqgJU28xNsscFIXmFprG.sDMDRn3NpQDby4RTdRpZF_8o0oIwe1Vn0wGQ2pyihrYemg1Wq7v8st6WBMk9UPvTDyCbcoz_9.VscKhyL87nhexF.X30I.WURRn3LVTo3BjpOUzL.kOXS4j2oqsONhvks34YptqG6NOdMtCyo2dJhcCojSK9QUqU9mJQWqDfpdItC4QBuiwtYrfj9epV8JGkB8z3zUwutPpVbaiRyZ8MeySljHA5U5yoXZhzeu1DilpnAXoiYZaXoOwE0WY4nT_zqGWBl8pEHQq4bp.ryc2AWVy3BhrYDnZZ2BlDnWpYXOc34Ata0UIbPcPJxnWrbiB9BoYgqpchaPYTzGlTiIqnJxvOB_O9MEJayWBNtNpLm2Q',
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
                    '-H', 'cookie: _ga=GA1.1.611983894.1716478735; __PPU_puid=7372220048289729256; UGVyc2lzdFN0b3JhZ2U=%7B%22CAIFRQ%22%3A%22ACZSQQAAAAAAAAAB%22%2C%22CAIFRT%22%3A%22ACZSQQAAAABncNdQ%22%2C%22MTIFRQ%22%3A%22ADO5uwAAAAAAAAAB%22%2C%22MTIFRT%22%3A%22ADO5uwAAAABncNdQ%22%7D; bnState_1871751={"impressions":1,"delayStarted":0}; hid=b3ac650730881e9e1d5c5e073b89d300; _ga_ECF2QFGQ9G=GS1.1.1735994610.15.0.1735994610.0.0.0; cf_clearance=qskGiffzDuD6YFS3fYw6VdzsMo62HfZLvHUd8vCa3yw-1735994615-1.2.1.1-i8ytuvtyOniXQwBOHj1sTCEqgJU28xNsscFIXmFprG.sDMDRn3NpQDby4RTdRpZF_8o0oIwe1Vn0wGQ2pyihrYemg1Wq7v8st6WBMk9UPvTDyCbcoz_9.VscKhyL87nhexF.X30I.WURRn3LVTo3BjpOUzL.kOXS4j2oqsONhvks34YptqG6NOdMtCyo2dJhcCojSK9QUqU9mJQWqDfpdItC4QBuiwtYrfj9epV8JGkB8z3zUwutPpVbaiRyZ8MeySljHA5U5yoXZhzeu1DilpnAXoiYZaXoOwE0WY4nT_zqGWBl8pEHQq4bp.ryc2AWVy3BhrYDnZZ2BlDnWpYXOc34Ata0UIbPcPJxnWrbiB9BoYgqpchaPYTzGlTiIqnJxvOB_O9MEJayWBNtNpLm2Q',
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

    