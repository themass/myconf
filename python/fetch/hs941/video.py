#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
import time
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
        print '940hs video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url = item['url']
                if i!=1:
                    url = "%s%s%s%s"%(item['url'],"index-",i,".html")
                print url
                self.videoParse(item['channel'], url)
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        ahrefs = self.header()
        channelList = []
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']="sp878"+obj['url']
            obj['showType']=3
            obj['channelType']='normal'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first("ul", {"class": "towmd widall videolist"})
        metas = div.findAll('li',{"class":"list_box box_homecon"})
        for meta in metas:
            obj = {}
            ahref = meta.first("a")
            mp4Url = self.parseDomVideo(ahref.get("href"))
            if mp4Url == None:
                print '没有mp4 文件:', ahref.get("href")
                continue
            obj['url'] = mp4Url
            obj['pic'] = meta.first('img').get("src")
            obj['name'] = meta.first('p').text.replace("&nbsp;","")
            print obj['name'],mp4Url,obj['pic']

            videourl = urlparse(obj['url'])
            obj['path'] = videourl.path
            obj['updateTime'] = datetime.datetime.now()
            obj['channel'] = channel
            if mp4Url.count(".m3u8")==0 and mp4Url.count(".mp4")==0:
                obj['videoType'] = "webview"
            else:
                obj['videoType'] = "normal"
            dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,obj['videoType'],baseurl)

        print 'sp878 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(url, header)
            divs = soup.findAll("div",{"class":"film_bar clearfix"})
            for div in divs:
                if div!=None:
                    ahrefs = div.findAll("a")
                    for ahref in ahrefs:
                        soup = self.fetchUrl(ahref.get("href"), header)
                        scripts = soup.findAll("script")
                        for script in scripts:
                            text = unquote(script.text).replace(" ","")
                            match = playVideo2.search(text)
                            if match!=None:
                                base = urlMap.get(match.group(1))
                                if base ==None:
                                    print 'urlMap 没有找到base',match.group(1),match.group(2)
                                    return None
                                return "%s%s%s"%(base,match.group(2),'.m3u8')
                            
                            match = playVideo.search(text)
                            if match!=None:
                                base = urlMap.get(match.group(1))
                                if base ==None:
                                    print 'urlMap 没有找到base',match.group(1),match.group(2)
                                    return None
                                return "%s%s%s"%(base,match.group(2),'.m3u8')
                           
                            match = playVideo3.search(text)
                            if match!=None:
                                base = urlMap.get(match.group(1))
                                if base ==None:
                                    print 'urlMap 没有找到base',match.group(1),match.group(2)
                                    return None
                                return "%s%s"%(base,match.group(2))
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
if __name__ == '__main__':
    videop  = VideoParse()
    print videop.parseDomVideo("/Html/89/3075.html")
    
    