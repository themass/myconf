#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
import time,json
from fetch.profile import *
from urllib import unquote

class VideoParse(BaseParse):

    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoChannel(item)
        print 'cd1988 video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, item['page']):
                url= item['url']
                if i!=1:
                    url= "%s%s%s"%(item['url'].replace('.html','-'),i,".html")
                self.videoParse(item['channel'], url)
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        soup = self.fetchUrl("/type1/-----addtime.html")
        div = soup.first("div",{"id":"j-nav-type1"})
        ahrefs = div.findAll("a")
        channelList = []
#         for ahref in ahrefs:
#             if ahref.text!="全部":
#                 obj={}
#                 obj['url']=ahref.get('href')
#                 obj['baseurl']=baseurl
#                 obj['updateTime']=datetime.datetime.now()
#                 obj['pic']=''
#                 obj['rate']=0.7
#                 obj['channel']=obj['name']=ahref.text+"片"
#                 obj['showType']=1
#                 obj['channelType']='movie'
#                 obj['page']=20
#                 channelList.append(obj)
                
        obj={}
        obj['url']='/vod-show-id-10.html'
        obj['baseurl']=baseurl
        obj['updateTime']=datetime.datetime.now()
        obj['pic']=''
        obj['rate']=0.7
        obj['channel']=obj['name']='美女福利'
        obj['showType']=1
        obj['channelType']='movie'
        obj['page']=80
        channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        lis = soup.findAll("div",{"class":'li_li clearfix'})
        for li in lis:
            ahref = li.first('a')
            if ahref != None:
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                img = ahref.first("img")
                obj['pic'] =img.get("src")
                obj['name'] = li.first('p',{"class":"name"}).text
                obj['path'] = "%s%s%s"%(channel,"-",obj['name'])
                obj['updateTime'] = datetime.datetime.now()
                if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                    obj['videoType'] = "webview"
                else:
                    obj['videoType'] = "normal"
                obj['channel'] = channel
                obj['baseurl'] = baseurl
                print obj['videoType'],obj['url'],obj['pic']
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,obj['videoType'],baseurl)

        print 'cd1988 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
      
        try:
            soup = self.fetchUrl(url)
            div = soup.first("div",{"class":"playlist"})
            if div!=None:
                aherf = div.first("a")
                if aherf !=None:
                    soup = self.fetchUrl(aherf.get('href'))
                    playerall = soup.first("div",{"class":"playerall"})
                    script  = playerall.first("script")
                    if script !=None:
                        url = script.get("src")
                        content = unquote(str(script.text))
                        if url!=None:
                            content = self.fetchContentUrlWithBase(script.get("src"))
                            content = unquote(str(content))
                        match = regVideo.search(content)
                        if match!=None:
                            obj = json.loads(match.group(1))
                            return obj.get('url',None)
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
