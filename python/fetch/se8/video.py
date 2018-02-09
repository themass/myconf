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
            for i in range(1, maxVideoPage):
                self.videoParse(
                    item['channel'], item['url'] + str(i)+'.htm')
                print '解析页数 ', item['url'], ' ---', i, '完成'
    
    def videoChannel(self):
        soup = self.fetchUrl(self.t_obj['url'])
        tds = soup.findAll('td')
        channelList =[]
        for td in tds:
            ahref = td.first('a')
            if ahref == None:
                print '没有频道'
                continue
            obj={}
            obj['name']='超爽自拍'
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=td.first('img').get('src')
            obj['rate']=1.2
            obj['showType']=3
            obj['channel']="www.233cf.com"+ahref.get('href')
            obj['showType']=3
            obj['channelType']='fanqiang'
            channelList.append(obj)
        return channelList
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
                    obj['url'] = mp4Url
                    img = li.first("img")
                    obj['pic'] = img.get('src')
                    obj['name'] = li.first("h3").text
                    print obj['name'],li.first("h3"),mp4Url
    
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
            divs = soup.findAll("div",{"class":"mox"})
            for div in divs:
                SPAN = div.first("span")
                if SPAN!=None:
                    if SPAN.text=='在线播放':
                        soup = self.fetchUrl(div.first("a").get("href"))
                        scripts = soup.findAll("script", {"type": "text/javascript"})
                        for s in scripts:
                            match = m3u8regVideo.search(s.text)
                            if match!=None:
                                print '--------',match.group(2)
                                return urlMap.get(match.group(1))+str(match.group(2))
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
