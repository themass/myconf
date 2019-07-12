#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
import time
from fetch.profile import *
class VideoUserParse(BaseParse):

    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoUser(item)
        print 'shixunziyuan user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url = item['url']
                if i!=1:
                    url= "%s%s%s%s"%(item['url'],"index_",i,".html")
                print url
                self.videoParse(item['channel'], url,item['userId'])
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        ahrefs = self.header6()
        channelList = []
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl8
            obj['updateTime']=datetime.datetime.now()
            obj['pic']='' 
            obj['rate']=1.2
            obj['channel']='shuimi_all'
            obj['userId']='shuimi_'+ahref.text
            obj['showType']=3
            obj['channelType']='normal'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrlWithBase(baseurl8+url, header3)
        div = soup.first("div",{"class":"box movie2_list"})
        if div!=None:
            lis = div.findAll("li")
            for li in lis:
                #name,pic,url,userId,rate,updateTime,path
                ahref = li.first("a")
                if ahref!=None:
                    obj = {}
                    mp4Url = self.parseDomVideo(ahref.get("href"))
                    if mp4Url == None:
                        print '没有mp4 文件:', ahref.get("href")
                        continue
                    obj['url'] = mp4Url
                    obj['pic'] = ahref.first('img').get("src")
                    obj['name'] = ahref.first('h3').text
        
                    videourl = urlparse(obj['url'])
                    obj['path'] = "shuimi_"+videourl.path
                    obj['rate'] = 1.2
                    obj['updateTime'] = datetime.datetime.now()
                    obj['userId'] = userId
                    obj['baseUrl'] = baseurl8
                    obj['showType'] = 3
                    if obj['url'].count("m3u8")==0 and obj['url'].count("mp4")==0:
                        obj['videoType'] = "webview"
                    else:
                        obj['videoType'] = "normal"
                    print obj['videoType'],obj['name'],mp4Url,obj['pic']
                    dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideoUserItem(obj)

        print 'shuimi video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrlWithBase(baseurl8+url, header3)
            scripts = soup.findAll("script")
            for script in scripts:
                text = unquote(script.text).replace('" + HOST+ "', "9873.sinaxicdn.com")
                texts = text.split(";")
                for item in texts:
                    match = regVideo2.search(item)
                    if match!=None:
                        return "%s%s%s"%("http",match.group(1),'.m3u8')
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

