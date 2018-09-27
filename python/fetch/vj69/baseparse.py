#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
import threading
from common.envmod import *
from common import db_ops
import threading
from BeautifulSoup import BeautifulSoup
# http://www.dehyc.com
baseurl = "https://69vj.com"
channel = '69vj.comweb_self_69vj'
header = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": "https://69vj.com/wp-content/plugins/kt/player/player.php","cookie": "_ga=GA1.2.1252287725.1537975339; _gid=GA1.2.231187077.1537975339; __cfduid=db12ea19586677296bf9195b2402aecf31537975345; _gat=1"}
videoUrl = 'https://69vj.com/page/%s'
maxCount = 3


class BaseParse(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def fetchUrl(self, url, aheader=header):
        count = 0
        while count < maxCount:
            try:
                req = urllib2.Request(url, headers=aheader)
                content = urllib2.urlopen(req, timeout=300).read()
                soup = BeautifulSoup(content)
                return soup
            except Exception as e:
                print '打开页面错误,重试', url, '次数', count
                count = count + 1

        print '打开页面错误,重试3次还是错误', url
        return BeautifulSoup('')
