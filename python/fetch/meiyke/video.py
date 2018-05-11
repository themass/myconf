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
        print 'duotv video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, item['page']):
                url= item['url']
                if i!=1:
                    url= "%s%s%s"%(item['url'].replace('1.html',''),i,".html")
                self.videoParse(item['channel'], url)
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        soup = self.fetchUrl('/')
        div  = soup.first('ul',{'class':'h_nav_chn_ul'})
        channelList =[]
        if div!=None:
            ahrefs = div.findAll('a')
            for ahref in ahrefs:
                if ahref.text!='首页':
                    obj={}
                    obj['name']=ahref.text
                    obj['url']=ahref.get('href')
                    obj['baseurl']=baseurl
                    obj['updateTime']=datetime.datetime.now()
                    obj['pic']=''
                    obj['rate']=0.7
                    obj['channel']=obj['name']=ahref.text
                    obj['showType']=1
                    obj['channelType']='movie'
                    channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first("ul",{"class":'the-list cf'})
        lis = div.findAll("li")
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
                obj['name'] = img.get("alt").replace("免费","").replace("电影","").replace("在线看","").replace("观看","").replace("高清","").replace("完整版","").replace("手机","").replace("在线","")
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
#         for obj in dataList:
#             ops.inertVideo(obj,obj['videoType'],baseurl)

        print 'duotv video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
      
        try:
            soup = self.fetchUrl(url)
            iframe = soup.first("iframe")
            if iframe!=None:
                aherf = iframe.get("src")
                shell = "%s %s"%("wget ",aherf)
                ret = os.popen(shell).read()
                if len(ret)>0:
                    for item in ret:
                        item = unquote(str(item))
                        match = regVideo.search(item)
                        if match!=None:
                            return 'http'+match.group(1)
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
