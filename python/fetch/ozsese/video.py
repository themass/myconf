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
        for k,v in channels.items(): 
            for i in range(1, maxVideoPage):
                self.videoParse(k, v % (i))

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
            obj['path'] = videourl.query
            obj['updateTime'] = datetime.datetime.now()
            obj['channel'] = channel
            obj['videoType'] = 'normal'
            obj['baseurl'] = baseurl
            dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,obj['videoType'],baseurl)
        print 'ozsese video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
    # 下面是抓取具体mp4文件的
#         header = {'User-Agent':
#                   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            soup = self.fetchUrl(url, header)
            source = soup.first("source")
            if source == None:
                print '没找到mp4'
                return None
            return source.get("src")
        except Exception as e:
            common.format_exception(e)
            return None

