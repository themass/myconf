#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from fetch.profile import *

class VideoParse(BaseParse):

    def __init__(self, obj):
        self.t_obj = obj

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        ops.inertVideoChannel(self.t_obj)
        dbVPN.commit()
        for i in range(1, maxVideoPage):
            self.videoParse(
                self.t_obj['channel'], (self.t_obj['url'] + "/p/%s") % (i))
            print '解析完成 ', self.t_obj['url'], ' ---', i, '页'

    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first("div", {"class": "detail_right_div"})
        if div != None:
            ul = div.first('ul')
            if ul != None:
                lis = ul.findAll('li')
                for li in lis:
                    obj = {}
                    ahref = li.first("a")
                    if ahref != None:
                        mp4Url = self.parseDomVideo(ahref.get("href"))
                        if mp4Url == None:
                            print '没有mp4 文件:', ahref.get("href")
                            continue
                        obj['url'] = mp4Url
                    img = li.first("img")
                    obj['pic'] = img.get('data-original')
                    obj['name'] = img.get('title')
                    print img.get('title')

                    videourl = urlparse(obj['url'])
                    obj['path'] = videourl.path
                    obj['updateTime'] = datetime.datetime.now()
                    obj['channel'] = channel
                    dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj)

        print 'yezmw video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            soup = self.fetchUrl(url, header)
            dz = soup.first("div", {"class": "dz"})
            if dz == None:
                return None
            return dz.first('p').text
        except Exception as e:
            common.format_exception(e)
            return None


def videoParse(queue):
    queue.put(VideoParse())
