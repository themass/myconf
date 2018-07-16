#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common, httputil
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
        print '52cjg video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url = item['url']
                if i!=1:
                    url= "%s%s%s"%(url,"?page=",i)
                print url
                self.videoParse(item['channel'], url)
                print '解析完成 ', item['baseurl'],item['channel'], ' ---', i, '页'
                time.sleep(1)
    def videoChannel(self):
        channelList = []
        ahrefs = self.header("header.html")
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1
            obj['channel']='52cjg'+ahref.text
            obj['showType']=3
            obj['channelType']='52cjg_all'
            channelList.append(obj)
        channelList.reverse()
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        metas = soup.findAll("div",{"class":"x3 margin-top"})
        for meta in metas:
            obj = {}
            ahref = meta.first("a")
            mp4Url = self.parseDomVideo(ahref.get("href"))
            if mp4Url == None:
                print '没有mp4 文件:', ahref.get("href")
                continue
            obj['url'] = mp4Url
            img = meta.first("img")
            obj['pic'] = baseurl+img.get("src")
            obj['name'] = img.get("alt")

            videourl = urlparse(mp4Url)
            obj['path'] = '52cjg_'+videourl.path
            obj['updateTime'] = datetime.datetime.now()
            obj['channel'] = channel
            obj['videoType'] = "normal"
            obj['baseurl'] = baseurl
            print obj['name'],obj['videoType'],obj['url'],obj['pic']
            dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
#         for obj in dataList:
#             ops.inertVideo(obj,obj['videoType'],baseurl)

        print 'qh video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(url)
            scripts = soup.findAll('script')
            for script in scripts:
                text = unquote(script.text)
                texts = text.split(";")
                for item in texts:
                    match = regVideo.search(item)
                    if match!=None:
                        param = {}
                        param['id']=match.group(1)
                        param['td']=match.group(2)
                        videoUrlm3 = httputil.postData(videoUrl, param, videoHeader)
                        return videoUrlm3
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
