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
        chs  = self.videoChannel()
        for ch in chs:
            ops.inertVideoChannel(ch)
        print ' channel ok; len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for ch in chs:
            for i in range(20, maxVideoPage):
                url= ch['url']
                if i!=1:
                    url= "%s%s%s%s"%(ch['url'],"index-",i,'.html')
                self.videoParse(ch['channel'], url)
                print '解析完成 ', ch['channel'], ' ---', i, '页'
    def videoChannel(self):
        objs = []
        obj={}
        obj['name']="韩国R级"
        obj['url']=baseurlR
        obj['baseurl']=baseurl
        obj['updateTime']=datetime.datetime.now()
        obj['pic']=''
        obj['rate']=1.2
        obj['channel']=obj['name']
        obj['showType']=3
        obj['channelType']='movie'
        objs.append(obj)
        return  objs
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrlWithBase(url)
        alist = soup.findAll("a", {"class": "link"})
        for ahref in alist:
            mp4Url  = self.parseDomVideo(ahref.get("href"))
            if mp4Url==None:
                continue
            if mp4Url.count('.html')!=0 :
                print mp4Url,"爱奇艺，忽略"
                continue
            obj = {}
            obj['url'] = mp4Url
            img = ahref.first("img")
            obj['pic'] = img.get('data-original')
            obj['name'] = ahref.get('title')
            print obj['name'],mp4Url,obj['pic']

            obj['path'] = obj['name']+channel
            obj['updateTime'] = datetime.datetime.now()
            obj['channel'] = channel
            dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,"normal",baseurl)

        print 'seman video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            soup = self.fetchUrl(url, header)
            divplay = soup.first('div',{"class":"playlist"})
            if divplay!=None:
                h3 = divplay.first('h3',{"class":"from"})
                if h3!=None and h3.text=='极速云播':
                    div = soup.first('div',{"class":'stab_list'})
                    if div!=None:
                        ahref = div.first('a')
                        if ahref!=None:
                            soup = self.fetchUrl(ahref.get('href'), header)
                            scripts = soup.findAll("script")
                            for script in scripts:
                                text = script.get('src',"")
                                if text.count("upload/playdata")!=0:
                                    js = self.fetchContentUrlWithBase(baseurl+text, header)
                                    match = videoApi.search(unquote(js))
                                    if match!=None:
                                        str= match.group(1).replace(")","").replace("(","").replace("'","")
                                        alist = str.split("$")
                                        if len(alist)>1:
                                            return "%s%s"%(jsurl,alist[len(alist)-1])
                                        return "%s%s"%(jsurl,alist[0])
            print url,'没有mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
