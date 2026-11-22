#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import threading
import os
import re
import sys
import time
import cloudscraper
from common.envmod import *
from common import db_ops
from common import common
from BeautifulSoup import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf8')

baseurl = "https://91porny.com"
maxCount = 3
regVideo = re.compile(r'http(.*?)m3u8')
namereg = re.compile(r"(&#[0-9]*;)+")

# 复用 scraper；不要覆盖 UA，否则 Cloudflare 会 403
_scraper = None
_scraper_ready = False


def get_scraper():
    global _scraper, _scraper_ready
    if _scraper is None:
        _scraper = cloudscraper.create_scraper()
    if not _scraper_ready:
        try:
            _scraper.get(baseurl + '/', timeout=60)
            time.sleep(0.3)
            _scraper_ready = True
        except Exception as e:
            print '首页预热失败', common.format_exception(e)
    return _scraper


class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def _full_url(self, url):
        if not url:
            return baseurl
        if url.startswith('http'):
            return url
        return baseurl + url

    def _is_cf_challenge(self, text):
        if not text:
            return True
        return 'Just a moment' in text

    def fetchUrl(self, url):
        global _scraper, _scraper_ready
        count = 0
        full = self._full_url(url)
        while count < maxCount:
            try:
                scraper = get_scraper()
                resp = scraper.get(full, timeout=60)
                text = resp.text
                if self._is_cf_challenge(text):
                    _scraper = None
                    _scraper_ready = False
                    raise Exception('cloudflare challenge status=%s' % resp.status_code)
                return BeautifulSoup(text)
            except Exception as e:
                print common.format_exception(e)
                print '打开页面错误,重试', full, '次数', count
                count = count + 1
                time.sleep(1 + count)
        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')

    def header(self):
        content = ''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__))
        with open("porna91/header.html") as f:
            for line in f.readlines():
                content = "%s%s" % (content, line)
        soup = BeautifulSoup(content)
        return soup.findAll('a')

    def header2(self):
        content = ''
        print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__))
        with open("porna91/header2.html") as f:
            for line in f.readlines():
                content = "%s%s" % (content, line)
        soup = BeautifulSoup(content)
        return soup.findAll('a')
