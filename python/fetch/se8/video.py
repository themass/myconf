#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from fetch.profile import *

class VideoParse(BaseParse):

    def __init__(self,obj):
        self.t_obj=obj
        

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoChannel(item)
        print 'se8 video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            try:
                for i in range(1, maxVideoPage):
                    if item['url'].count('短视频')>0:
                        continue
                    url = item['url']
                    if i!=1:
                        url = "%s%s%s"%(url.replace(".html", "-"),i,".html")
                    if item['url'].count('女优专辑')>0:
                        print '解析女友专辑'
                        con = self.nvviderPaser(item['channel'], url)
                        if con==False:
                            print '没有数据了啊-======页数',i,'---',item['name'],item['url']
                            break
                    else:
                        con = self.videoParse(
                            item['channel'], url)
                        if con==False:
                            print '没有数据了啊-======页数',i,'---',item['name'],item['url']
                            break
                    print '解析页数 ', item['url'], ' ---', i, '完成'
            except Exception as e:
                pass
    def videoChannel(self):
        channelList =[]
        obj={}
        obj['name']='超爽自拍'
        obj['url']=self.t_obj['url']
        obj['baseurl']=baseurl
        obj['updateTime']=datetime.datetime.now()
        obj['pic'] = ''
        obj['rate']=1.2
        obj['showType']=3
        obj['channel']="www.233cf.com"+self.t_obj['url']
        obj['showType']=3
        obj['channelType']='normal'
        channelList.append(obj)
        channelList.reverse()
        return channelList
    def nvviderPaser(self, channel, url):
        soup = self.fetchUrl(url)
        div = soup.first("div", {"class": "text-list-html "})
        if div!=None:
            lis = div.findAll('li')
            if len(lis)==0:
                return False
            for li in lis:
                ahref = li.first('a')
                if ahref != None:
                    for i in range(1, 10):
                        try:
                            print '解析女优频道',channel,ahref.get('href'),ahref.get('title'),i
                            url = ahref.get('href')
                            if i!=1:
                                url = "%s%s%s"%(ahref.replace(".html", "-"),i,".html")
                            self.videoParse(channel, url)
                        except Exception as e:
                            pass
            return True           
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first("div", {"class": "text-list-html "})
        if div!=None:
            lis = div.findAll('li')
            if len(lis)==0:
                return False
            for li in lis:
                ahref = li.first('a')
                if ahref != None:
                    obj = {}
                    mp4Url = self.parseDomVideo(ahref.get("href"))
                    if mp4Url == None:
                        print 'MP4url', ahref.get("href")
                        continue
                    obj['url'] = mp4Url
                    img = li.first("img")
                    if img.get("data-original")==None:
                        if img.get('src').count("http")>0:
                            obj['pic']=img.get('src')
                        else:
                            obj['pic']=baseurl+img.get('src')
                    else:
                        obj['pic']=img.get('data-original')
                    obj['name'] = ahref.get("title")
                    print obj['name'],mp4Url,obj['pic']
    
                    videourl = urlparse(obj['url'])
                    obj['path'] = videourl.path
                    obj['updateTime'] = datetime.datetime.now()
                    obj['channel'] = channel
                    obj['baseurl'] = baseurl
                    obj['videoType'] = 'normal'
                    dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,"normal",baseurl)

        print 'se8 video -- ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        return True
    
    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            soup = self.fetchUrl(url)
            divs = soup.findAll("div",{"id":"playlist4"})
            for div in divs:
                aherf = div.first("a")
                if aherf!=None:
                    soup = self.fetchUrl(aherf.get("href"))
                    scripts = soup.findAll("script")
                    for s in scripts:
                        match = m3u8regVideo.search(s.text.replace(" ",""))
                        if match!=None:
                            return "https://s2.cdn-23147ed7c1b03e86.com%s.m3u8"%(match.group(1))
#                             if m3u8Map.get(match.group(1)) !=None:
#                                 return m3u8Map.get(match.group(1))+str(match.group(2))
                    for s in scripts:
                        match = mp4regVideo.search(s.text.replace(" ",""))
                        if match!=None:
                            return "https://jccfy.com%s.mp4"%(match.group(1))
            scripts = soup.findAll("script", {"type": "text/javascript"})
            for s in scripts:
                match = regVideo.search(s.text)
                if match!=None:
                    print '--------',match.group(2)
                    return urlMap.get(match.group(1))+str(match.group(2))
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None


def videoParse(queue):
    queue.put(VideoParse())
