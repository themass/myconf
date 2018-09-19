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
                    url = item['url']
                    if i!=1:
                        url = "%s%s%s"%(url.replace(".html", "-"),i,".html")
                    self.videoParse(
                        item['channel'], url)
                    print '解析页数 ', item['url'], ' ---', i, '完成'
            except Exception as e:
                pass
    def videoChannel(self):
        soup = self.fetchUrl(self.t_obj['url'])
        tds = soup.first('div',{"class":"row category-content"})
        channelList =[]
        if tds!=None:
            alist = tds.findAll("a")
            for ahref in alist:
                obj={}
                obj['name']='超爽自拍'
                obj['url']=ahref.get('href')
                obj['baseurl']=baseurl
                obj['updateTime']=datetime.datetime.now()
                img = ahref.first('img')
                if img.get("data-original")==None:
                    obj['pic']=baseurl+img.get('src')
                else:
                    obj['pic']=img.get('data-original')
                obj['rate']=1.2
                obj['showType']=3
                obj['channel']="www.233cf.com"+ahref.get('href')
                obj['showType']=3
                obj['channelType']='normal'
                channelList.append(obj)
        channelList.reverse()
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first("div", {"class": "text-list-html "})
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
                    obj['url'] = mp4Url
                    img = li.first("img")
                    if img.get("data-original")==None:
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
                            return mp4Url+str(match.group(1))
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
