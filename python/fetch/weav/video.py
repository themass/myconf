#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common


class VideoParse(BaseParse):

    def __init__(self):
        pass

    def run(self):
        for i in range(1, maxPage):
            self.videoParse(
                channel, videoUrl + str(i))
            print '解析页数 ', videoUrl, ' ---', i, '完成'

    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        divs = soup.findAll("div", {"class": "col-sm-6 col-md-4 col-lg-4"})
        for div in divs:
            ahref = div.first('a')
            if ahref != None:
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print 'MP4url', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                img = div.first("img")
                obj['pic'] = img.get('src')
                obj['name'] = img.get('title')
                print img.get('title')

                videourl = urlparse(obj['url'])
                obj['path'] = videourl.path
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                obj['videoType'] = 'normal'
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj)

        print 'weav video -- ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            print url
            soup = self.fetchUrl(url, header)
            textarea = soup.first("textarea", {"name": "video_embed_code"})
            if textarea == None:
                return None
            match = regVideo.search(textarea.text)
            print textarea.text, match
            if match == None:
                return None
            print match.group(1)
            soup = self.fetchUrlWithBase(match.group(1), header)
            videoUrl = soup.first("source")
            if videoUrl == None:
                return None
            return videoUrl.get("src")
        except Exception as e:
            common.format_exception(e)
            return None


def videoParse(queue):
    queue.put(VideoParse())
