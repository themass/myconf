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
        divs = soup.findAll("div", {"class": "block"})
        for div in divs:
            obj = {}
            divImg = div.first("div", {"class": "media-image"})
            if divImg != None:
                ahref = div.first("a")
                if ahref != None:
                    mp4Url = self.parseDomVideo(ahref.get("href"))
                    if mp4Url == None:
                        print '没有mp4 文件:', ahref.get("href")
                        continue
                    obj['url'] = mp4Url
                    img = ahref.first("img")
                    if img != None:
                        picUrl = baseurl + img.get('data-src')
                        obj['pic'] = picUrl
            divTitle = div.first("div", {"class": "block-layer block-inner"})
            name = divTitle.first('a').text
            obj['name'] = name
            videourl = urlparse(obj['url'])
            obj['path'] = videourl.path
            obj['updateTime'] = datetime.datetime.now()
            obj['channel'] = channel
            obj['baseurl'] = baseurl
            print obj['name'],mp4Url,obj['pic']

            dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,"normal",baseurl)

        print 'singlove video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            soup = self.fetchUrl(url, header)
            iframe = soup.first("iframe")
            if iframe == None:
                return None
            url = iframe.get("src")
            header = {'User-Agent':
                      'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}

            soup = self.fetchUrlWithBase(url, header)
            source = soup.first("source")
            if source == None:
                return None
            return source.get("src")
        except Exception as e:
            common.format_exception(e)
            return None


def videoParse(queue):
    queue.put(VideoParse())
