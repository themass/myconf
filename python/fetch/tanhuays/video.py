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

    names = ''
    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoChannel(item)
        print 'tanhuays video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            url= item['url']
            for i in range(1, maxVideoPage):
                con = self.videoParse(item['channel'], item['channelType'],'%s%s%s'%(url.replace('-1/','-'),i,'/'))
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
            obj['channel']='tanhuays'+ahref.text
            obj['showType']=3
            obj['channelType']='tanhuays_all'
            channelList.append(obj)
#         channelList.reverse()
        return  channelList
    def videoParse(self, channel, channelType, url):
        dataList = []
        nameTemp = ''
        soup = self.fetchUrl(url)
        div = soup.first('ul',{"class":"myui-myui-vodlist clearfix"})
        if div!=None:
            divs = div.findAll("div",{"class":"myui-vodlist__box"})
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
                    obj['pic'] = baseurl+ahref.get('data-original')
                    obj['name'] = ahref.get("title")

                    obj['path'] = 'tanhuays'+ahref.get("href")
                    obj['updateTime'] = datetime.datetime.now()
                    obj['channel'] = channel
                    obj['baseurl'] = baseurl+ahref.get("href")
                    print obj['name'],obj['url'],obj['pic'],obj['baseurl']
                    dataList.append(obj)
                    nameTemp= nameTemp+obj['name']
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for i in range(1, 3):
            try:
                for obj in dataList:
                    ops.inertVideo(obj,"normal",baseurl,channelType)
                break
            except Exception as e:
                print common.format_exception(e)
        print '51md video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        if nameTemp == self.names:
            print nameTemp
            return False
        else:
            self.names = nameTemp
        return True
    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(url)
            div = soup.first("div",{'div':'yui-player__video border-radius embed-responsive clearfix'})
            if div != None:
                texts = div.text.replace(' ','').replace('\\',"").replace('\/','/').split(',')
                for item in texts:
                    match = regVideo.search(item)
                    if match!=None:
                        path = match.group(1)
                        if path.count('www.formax23')!=0:
                            print '没找到mp4'
                            return None
                        return 'http'+path+'index.m3u8'

            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
