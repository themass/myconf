#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
import threading
from common.envmod import *
from common import db_ops
from common import common
import threading
from BeautifulSoup import BeautifulSoup
import re
# http://www.dehyc.com
baseurl = "https://weav.cc"
videoUrl = "/videos?page="
channel = 'weav.cc    self_weav'
header = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl}
maxCount = 3
regVideo = re.compile(r'src="(.*)" frameborder=')


class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url, aheader=header):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(baseurl + url, headers=aheader)
                content = urllib2.urlopen(req, timeout=300).read()
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '鎵撳紑椤甸潰閿欒,閲嶈瘯', baseurl + url, '娆℃暟', count
                count = count + 1

        print '鎵撳紑椤甸潰閿欒,閲嶈瘯3娆¤繕鏄敊璇�', url
        return BeautifulSoup('')

    def fetchUrlWithBase(self, url, aheader=header):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(url, headers=aheader)
                content = urllib2.urlopen(req, timeout=300).read()
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print common.format_exception(e)
                print '鎵撳紑椤甸潰閿欒,閲嶈瘯', url, '娆℃暟', count
                count = count + 1

        print '鎵撳紑椤甸潰閿欒,閲嶈瘯3娆¤繕鏄敊璇�', url
        return BeautifulSoup('')

    def fetchContentUrlWithBase(self, url, aheader=header):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(url, headers=aheader)
                content = urllib2.urlopen(req, timeout=300).read()
                return content
            except Exception as e:
                print common.format_exception(e)
                print '鎵撳紑椤甸潰閿欒,閲嶈瘯', url, '娆℃暟', count
                count = count + 1

        print '鎵撳紑椤甸潰閿欒,閲嶈瘯3娆¤繕鏄敊璇�', url
        return ''
