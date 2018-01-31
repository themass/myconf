#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from fetch.profile import *

class VideoParse(BaseParse):

    def __init__(self):
        pass

    def run(self):
        for i in range(1, maxVideoPage):
            self.videoParse(channel, videoUrl % (i))

    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        aList = soup.findAll("a", {"rel": "bookmark"})
        for aItem in aList:
            obj = {}
            mp4Url = self.parseDomVideo(aItem.get("href"))
            if mp4Url == None:
                print '没有mp4 文件:', aItem.get("href")
                continue
            obj['url'] = mp4Url
            img = aItem.first("img").get("src")
            if img != None:
                obj['pic'] = img
            name = aItem.get("title")
            print name, mp4Url
            obj['name'] = name
            videourl = urlparse(obj['url'])
            obj['path'] = videourl.path
            obj['updateTime'] = datetime.datetime.now()
            obj['channel'] = channel
            dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj)

        print 'singlove video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            soup = self.fetchUrl(url, header)
            videoCode = soup.first("source", {"type": "video/mp4"})
            if videoCode == None:
                return None
            return videoCode.get("src")
        except Exception as e:
            common.format_exception(e)
            return None


def videoParse(queue):
    queue.put(VideoParse())
