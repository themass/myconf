#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from fetch.profile import *
from urllib import unquote
import sys,time
reload(sys)
# 
sys.setdefaultencoding('utf8')

class VideoParse(BaseParse):

    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoChannel(item)
        print 'jiu667 video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            url= item['url']
            channelType = item['channelType']
            for i in range(40, maxVideoPage):
                con = False
                if i==1:
                    con = self.videoParse(item['channel'], url,channelType)
                else:
                    con = self.videoParse(item['channel'], '%s%s%s'%(url.replace('index.html','list_'),maxVideoPage-i,'.html'),channelType)
                if con==False:
                    print '没有数据了啊-======页数',i,'---',item['name'],item['url']
                    break
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        channelList = []
        ahrefs = self.header()
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']='jiu667'+ahref.text
            obj['showType']=3
            obj['channelType']='jiu667_all'
            channelList.append(obj)
#         channelList.reverse()
        return  channelList
    def videoParse(self, channel, url,channelType):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first('div',{"class":"mod channel-list"})
        if div!=None:
            divs = div.findAll("dl")
            if len(divs)==0:
                return False
            for item in divs:
                ahref = item.first('a')
                if ahref != None:
                    obj = {}
                    mp4Url = self.parseDomVideo(ahref.get("href"))
                    if mp4Url == None:
                        print '没有mp4 文件:', ahref.get("href")
                        continue
                    obj['url'] = mp4Url
                    img = ahref.first('img')
                    obj['pic'] = baseurl+img.get('data-original')
#                     item.first('h3').text.replace(" ","")
                    obj['name'] = ahref.get('title')
                    print obj['name'],obj['url'],obj['pic']
    
                    videourl = urlparse(obj['url'])
                    obj['path'] = "jiu667_"+videourl.path
                    obj['updateTime'] = datetime.datetime.now()
                    obj['channel'] = channel
                    obj['baseurl'] = baseurl
                    dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,"normal",baseurl,channelType)

        print 'jiu667 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        return True
    def parseDomVideo(self, url):
        try:
            if url.count("script")==0:
                soup = self.fetchUrl(url)
                scripts = soup.findAll("script")
                for s in scripts:
                    text = unquote(s.text)
                    texts = text.split(';')
                    for item in texts:
                        match = regVideo.search(item)
                        if match!=None:
                            return 'http'+match.group(1)+'m3u8'
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
