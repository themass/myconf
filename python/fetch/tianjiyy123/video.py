#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
import time
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
        print 'tianjiyy123 video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= "%s%s%s"%(item['url'].replace('1-------.html',''),i,"---0-0---.html")
                self.videoParse(item['channel'], url)
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        soup = self.fetchUrl('/dianying/')
        div  = soup.first('dd',{'class':'clearfix'})
        channelList =[]
        if div!=None:
            ahrefs = div.findAll('a')
            for ahref in ahrefs:
                if ahref.text.count("动作")>0:
                    continue
                obj={}
                obj['name']=ahref.text
                obj['url']=ahref.get('href')
                obj['baseurl']=baseurl
                obj['updateTime']=datetime.datetime.now()
                obj['pic']=''
                obj['rate']=1.2
                obj['channel']=ahref.text
                obj['showType']=3
                obj['channelType']='movie'
                channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        lis = soup.findAll("li",{"class":'col-md-2 col-sm-3 col-xs-4'})
        for li in lis:
            ahref = li.first('a')
            if ahref != None:
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                obj['pic'] = ahref.get("data-original")
                obj['name'] = ahref.get("title")
                obj['path'] = "%s%s%s"%(channel,"-",obj['name'])
                print obj['path'],obj['url'],obj['pic']
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                obj['baseurl'] = baseurl
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,"normal",baseurl)

        print 'tianjiyy123 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            soup = self.fetchUrl(url, header)
            playlist1 = soup.first("div",{'id':'playlist1'})
            if playlist1!=None:
                ahref = playlist1.first('a')
                if ahref!=None:
                    soup = self.fetchUrl(ahref.get('href'), header)
                    div = soup.first('div',{'class':"info clearfix"})
                    if div!=None:
                        #play = div.first("script").get("src")
                        #if play!=None:
                            #text = self.fetchContentUrlWithBase(baseurl+play, {})
                            #content = unquote(str(text)).split("$")
                        content = unquote(div.text).split("$")
                        for item in content:
                            match = regVideo.search(item)
                            if match!=None:
                                return "http"+match.group(1)+'m3u8'
                        for text in content:
                            match = videoApiMp4.search(text)
                            if match!=None:
                                str= match.group(1)
                                return "%s%s%s"%("http",str,".mp4")
                        for text in content:
                            match = shareVideo.search(text)
                            if match!=None:
                                return text.replace("'",'').replace(")",'').replace(";",'')
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
