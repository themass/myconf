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
        channelObj = self.videoChannel()
        ops.inertVideoChannel(channelObj)
        print ' channel ok;'
        dbVPN.commit()
        dbVPN.close()
        url= channelObj['url'].replace('.html','')
        for i in range(1, maxVideoPage):
            self.videoParse(channelObj['channel'], (url + "-%s.html") % (i))
            print '解析完成 ', channelObj['channel'], ' ---', i, '页'
    def videoChannel(self):
        obj={}
        obj['name']="韩国伦理"
        obj['url']=videolUrl
        obj['baseurl']=baseurl
        obj['updateTime']=datetime.datetime.now()
        obj['pic']=''
        obj['rate']=1.2
        obj['channel']=obj['name']
        obj['showType']=3
        obj['channelType']='movie'
        return  obj
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first("div", {"class": "channel"})
        if div!=None:
            ahrefs = div.findAll('a',{'class':'link'})
            for ahref in ahrefs:
                mp4UrlList  = self.parseDomVideo(ahref.get("href"))
                for i in range(0,len(mp4UrlList)):
                    obj = {}
                    obj['url'] = mp4UrlList[i]
                    img = ahref.first("img")
                    obj['pic'] = img.get('data-original')
                    obj['name'] = "%s-%s"%(ahref.get('title'),i)
                    print obj['name'],mp4UrlList[i],obj['pic']
    
                    videourl = urlparse(obj['url'])
                    obj['path'] = videourl.query
                    obj['updateTime'] = datetime.datetime.now()
                    obj['channel'] = channel
                    dataList.append(obj)
            dbVPN = db.DbVPN()
            ops = db_ops.DbOps(dbVPN)
            for obj in dataList:
                ops.inertVideo(obj,"webview")
    
            print 'nomsgus video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
            dbVPN.commit()
            dbVPN.close()
            time.sleep(5)

    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            urlList =[]
            soup = self.fetchUrl(url, header)
            ul = soup.first('ul',{"class":'clearfix'})
            if ul!=None:
                alist = ul.findAll('a')
                for ahref in alist:
                    soup = self.fetchUrl(ahref.get('href'), header)
                    div = soup.first("div",{'class':'player'})
                    if div!=None:
                        script = div.first('script')
                        if script!=None:
                            match = videoApi.search(script.text)
                            if match!=None:
                                u = "%s%s"%("http",match.group(1).replace('\\',"").replace('\"',""))
                                urlList.append(u)
            return urlList
        except Exception as e:
            print common.format_exception(e)
            return urlList

def videoParse(queue):
    queue.put(VideoParse())
