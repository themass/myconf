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
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoChannel(item)
        print 'xiaoluoli99 video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            url= item['url']
            for i in range(1, maxVideoPage):
                self.videoParse(item['channel'], (url + "%s") % (i))
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        channelList = []
        obj={}
        obj['name']='小萝莉在线'
        obj['url']='page/'
        obj['baseurl']=baseurl5
        obj['updateTime']=datetime.datetime.now()
        obj['pic']=''
        obj['rate']=1.2
        obj['channel']='xiaoluoli99_luoli'
        obj['showType']=3
        obj['channelType']='normal'
        channelList.append(obj)
        channelList.reverse()
        return  channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrlWithBase(baseurl5+url,header)
        div = soup.first('div',{"class":"update_area_content"})
        if div!=None:
            divs = div.findAll("li", {"class": "i_list list_n1 list-images-size"})
            for item in divs:
                ahref = item.first('a')
                if ahref != None:
                    obj = {}
                    mp4Url = self.parseDomVideo(ahref.get("href"))
                    if mp4Url == None:
                        print 'MP4url', ahref.get("href")
                        continue
                    obj['url'] = mp4Url
                    img = ahref.first("img")
                    if img.get("data-original")==None:
                        obj['pic']=baseurl+img.get('src')
                    else:
                        obj['pic']=img.get('data-original')
                    obj['name'] = img.get("alt")
                    print obj['name'],mp4Url,obj['pic']
    
                    videourl = urlparse(obj['url'])
                    obj['path'] = 'luoli_'+videourl.path
                    obj['updateTime'] = datetime.datetime.now()
                    obj['channel'] = channel
                    obj['baseurl'] = baseurl5
                    obj['videoType'] = 'normal'
                    dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,"normal",baseurl)

        print 'xiaoluoli99_luoli video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrlWithBase(url,header)
            video = soup.first("video",{"autoplay":"autoplay"})
            if video!=None:
                return video.get("src").replace("end=120","end=12000")
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
