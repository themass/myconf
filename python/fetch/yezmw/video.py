#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
from fetch.profile import *

class VideoParse(BaseParse):

    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoUser(item)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url = "%s/p/%s"%(item['url'],i)
                con = self.videoParse(item['channel'], url,item['userId'])
                if con==False:
                    print '没有数据了啊-======页数',i,'---',item['name'],item['url']
                    break
                print '解析完成 ', item['url'], ' ---', i, '页'
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
            obj['channel']='yezmw_all'
            obj['userId']='yezmw_'+ahref.text
            obj['showType']=3
            obj['channelType']='normal'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrl(url, header)
        div = soup.first("div",{"class":"detail_right_div"})
        if div!=None:
            lis = div.findAll("li")
            if len(lis)==0:
                return False
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
                    obj['pic'] = li.first('img').get("data-original")
                    name = li.first('img').get("title")
                    if li.first('img').get("title")==None:
                        name = "性爱教程"
                    obj['name'] = name
        
                    videourl = urlparse(obj['url'])
                    obj['path'] = "yezmw"+videourl.path
                    obj['rate'] = 1.2
                    obj['updateTime'] = datetime.datetime.now()
                    obj['userId'] = userId
                    obj['baseUrl'] = baseurl
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

        print 'shixunziyuan video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        return True
    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            soup = self.fetchUrl(url, header)
            dz = soup.findAll("script")
            for item in dz:
                texts = unquote(item.text).split(";")
                for text in texts: 
                    match = videoApi.search(text)
                    if match!=None:
                        str= match.group(1)
                        return "%s%s%s"%("http",str,".m3u8")
            return None
        except Exception as e:
            common.format_exception(e)
            return None


def videoParse(queue):
    queue.put(VideoParse())
