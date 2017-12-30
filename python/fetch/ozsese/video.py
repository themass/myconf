#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common


class VideoParse(BaseParse):

    def __init__(self, channel, url):
        self.t_channel = channel
        self.t_url = url

    def run(self):

        for i in range(1, maxPage):
            self.videoParse(self.t_channel, self.t_url % (i))

    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        divs = soup.findAll("div", {"class": "mdl-cell mdl-cell--3-col"})
        for div in divs:
            obj = {}
            ahref = div.first("a")
            if ahref != None:
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                img = ahref.first("img")
                if img != None:
                    picUrl = img.get('src')
                    obj['pic'] = picUrl
            spanTitle = div.first(
                "span", {"class": "demo-card-image__filename"})
            name = spanTitle.text
            print name
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

        print 'ozsese video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            soup = self.fetchUrl(url, header)
            source = soup.first("source ")
            if source == None:
                return None
            return source.get("src")
        except Exception as e:
            common.format_exception(e)
            return None


def videoParse(queue):
    for channel, url in channels.items():
        queue.put(VideoParse(channel, url))
