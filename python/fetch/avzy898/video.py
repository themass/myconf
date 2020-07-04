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
        print 'avzy898 video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            url= item['url']
            for i in range(1, maxVideoPage):
                con = self.videoParse(item['channel'], '%s%s%s'%(url.replace('.html','-pg-'),i,'.html'))
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
            obj['channel']='avzy898'+ahref.text
            obj['showType']=3
            obj['channelType']='avzy898_all'
            channelList.append(obj)
#         channelList.reverse()
        return  channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first('ul',{"class":"videoContent"})
        if div!=None:
            divs = div.findAll("li")
            if len(divs)==0:
                return False
            for item in divs:
                ahref = item.first('a')
                if ahref != None:
                    obj = {}
                    mp4Url = self.parseDomVideo(ahref.get("href"))
                    if mp4Url == None or len(mp4Url)==0:
                        print '没有mp4 文件:', ahref.get("href")
                        continue
                    obj['url'] = mp4Url.get('url')
                    obj['pic'] = mp4Url.get('pic')
#                     item.first('h3').text.replace(" ","")
                    obj['name'] = ahref.text
                    print obj['name'],obj['url'],obj['pic']
    
                    videourl = urlparse(obj['url'])
                    obj['path'] = "avzy898"+videourl.path
                    obj['updateTime'] = datetime.datetime.now()
                    obj['channel'] = channel
                    obj['baseurl'] = baseurl
                    dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,"normal",baseurl)

        print 'avzy898 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        return True
    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(url)
            div = soup.first('div',{"class":'play-wapper'})
            if div!=None:
                mp4url={}
                img = div.first('img')
                if img!=None:
                    mp4url['pic']=img.get('src')
                else:
                    mp4url['pic']=''
                input = div.first('input')
                if input!=None:
                    mp4url['url']=input.get('value')
                else:
                    return None
                return mp4url
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
