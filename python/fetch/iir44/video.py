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
        print '44iir video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= item['url']
                if i!=1:
                    url = "%s%s%s"%(url.replace('.html','-'),i,'.html')
                self.videoParse(item['channel'], url)
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        soup = self.fetchUrl('/')
        ul = soup.first('div',{'id':'menu'})
        channelList =[]
        if ul!=None:
            ahrefs = ul.findAll('a')
            for ahref in ahrefs:
                obj={}
                if ahref.get('href')=="/":
                    continue
                obj['name']=ahref.text
                obj['url']=ahref.get('href')
                obj['baseurl']=baseurl
                obj['updateTime']=datetime.datetime.now()
                obj['pic']=''
                obj['rate']=1.2
                obj['channel']=baseurl.replace("http://", "").replace("https://", "")+ahref.get('href')
                obj['showType']=3
                obj['channelType']='normal'
                channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
#         div = soup.first("ul", {"class": "list_videor"})
#         if div==None:
        div = soup.first("div", {"class": "list_video"})
        if div!=None:
            lis = div.findAll('li')
            for li in lis:
                ahref = li.first('a')
                if ahref != None:
                    obj = {}
                    mp4Url = self.parseDomVideo(ahref.get("href"))
                    if mp4Url == None:
                        print '没有mp4 文件:', ahref.get("href")
                        continue
                    obj['url'] = mp4Url
                    img = li.first("img")
                    obj['pic'] = img.get('src')
                    obj['name'] = img.get('alt')
                    print obj['name'],mp4Url,obj['pic']
    
                    videourl = urlparse(obj['url'])
                    obj['path'] = videourl.path
                    obj['updateTime'] = datetime.datetime.now()
                    obj['channel'] = channel
                    dataList.append(obj)
            dbVPN = db.DbVPN()
            ops = db_ops.DbOps(dbVPN)
            for obj in dataList:
                ops.inertVideo(obj,"normal",baseurl)
    
            print '44iir video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
            dbVPN.commit()
            dbVPN.close()

    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            soup = self.fetchUrl(url, header)
            div = soup.first("div",{'class':'playBar'})
            if div!=None:
                ahref = div.first('a')
                if ahref!=None:
                    soup = self.fetchUrl(ahref.get('href'), header)
                    play_video = soup.first('div',{'class':'play_video'})
                    if play_video!=None:
                        script = play_video.first('script')
                        if script!=None:
                            text = unquote(self.fetchContentUrl(script.get('src'), header))
                            match = regVideo.search(text)
                            if match!=None:
                                videoUrl =match.group(2)
                                return "%s%s%s"%("http",videoUrl,'m3u8')
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
