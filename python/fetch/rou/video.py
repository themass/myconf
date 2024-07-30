#!/usr/bin python
# -*- coding: utf-8 -*-
import json

from baseparse import *
from urlall import *
from urlparse import urlparse
from common import common
from common import httputil
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
        print 'rou video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            url= item['url']
            for i in range(1, maxVideoPage):
                con = self.videoParse(item['channel'], item['channelType'],'%s%s'%(url,i))
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
            obj['channel']='rou'+ahref.text
            obj['showType']=3
            obj['channelType']='rou_all'
            channelList.append(obj)
#         channelList.reverse()
        return  channelList
    def videoParse(self, channel, channelType, url):
        dataList = []
        soup = self.fetchUrl(url)
        divs = soup.findAll("div",{"class":"relative"})
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
                imgdiv = ahref.first('img')

                obj['pic'] = imgdiv.get("src")
#                     item.first('h3').text.replace(" ","")
                obj['name'] = imgdiv.get("alt")
                videourl = urlparse(obj['url'])
                obj['path'] = baseurl+ahref.get("href")
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                obj['baseurl'] = baseurl+ahref.get("href")
                print obj['name'],obj['url'],obj['pic'],obj['baseurl']
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for i in range(1, 3):
            try:
                for obj in dataList:
                    ops.inertVideo(obj,"normal",baseurl,channelType)
                break
            except Exception as e:
                print common.format_exception(e)
        print 'rou video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        return True
    def parseDomVideo(self, url):
        time.sleep(1)
        try:
            context = httputil.getText(url)
            jsonData = json.loads(context)
            m3u8url = jsonData.get("video").get("videoUrl")
            print m3u8url
            return m3u8url
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
