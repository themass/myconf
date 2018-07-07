#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from fetch.profile import *


class VideoRmbParse(BaseParse):

    def __init__(self,obj):
        self.t_obj=obj
        self.t_obj['updateTime']=datetime.datetime.now()
        self.t_obj['pic']=''
        self.t_obj['rate']=1.2
        self.t_obj['showType']=3
        self.t_obj['channel']="se8_"+obj['url']
        self.t_obj['showType']=3
        self.t_obj['channelType']='fanqiang'

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        ops.inertVideoChannel(self.t_obj)
        print 'se8 video -- channel ok;,len=1'
        dbVPN.commit()
        dbVPN.close()
        for i in range(1,maxVideoPage):
            self.videoParse(
                self.t_obj['channel'], self.t_obj['url'] + str(i)+'.htm')
            print '解析页数 ', self.t_obj['url'], ' ---', i, '完成'
    
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first("div", {"class": "box movie_list"})
        if div!=None:
            lis = div.findAll('li')
            for li in lis:
                ahref = li.first('a')
                if ahref != None:
                    obj = {}
                    mp4Url = self.parseDomVideo(ahref.get("href"))
                    if mp4Url == None:
                        print 'MP4url', ahref.get("href")
                        continue
                    print mp4Url
                    obj['url'] = mp4Url
                    img = li.first("img")
                    obj['pic'] = img.get('src')
                    obj['name'] = li.first("h3").text
                    print channel,obj['name'],mp4Url,obj['pic']
    
                    videourl = urlparse(obj['url'])
                    obj['path'] = videourl.path
                    obj['updateTime'] = datetime.datetime.now()
                    obj['channel'] = channel
                    obj['videoType'] = 'normal'
                    dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,"normal",baseurl)

        print 'se8 video -- ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            soup = self.fetchUrl(url)
            scripts = soup.findAll("script", {"type": "text/javascript"})
            for s in scripts:
                match = rmbregVideo.search(s.text)
                if match!=None:
                    return rmbvideoUrl+str(match.group(2))
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None


def videoParse(queue):
    queue.put(VideoRmbParse())
