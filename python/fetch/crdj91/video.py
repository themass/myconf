#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from fetch.profile import *
from urllib import unquote
import sys,time,json,re
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
        print '91pron1 video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            url= item['url']
            channelType = item['channelType']

            # 获取最大页码
            # 从第1页遍历到最大页码
            for i in range(1, maxVideoPage):
                # 页码递减：list_136.html, list_135.html ...
                page_num = i
                page_url = url
                if page_num > 1:
                    page_url = '%spage/%s/'%(url, page_num)
                con = self.videoParse(item['channel'], page_url, channelType)
                if con==False:
                    print '没有数据了 - 页数', i, '---', item['name'], item['url']
                    break
                print '解析完成 ', item['channel'], ' ---', i, '页 / 共'

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
            obj['channel']='cj91'+ahref.text
            obj['showType']=3
            obj['channelType']='cj91_all'
            channelList.append(obj)
        # channelList.reverse()
        return  channelList
    def videoParse(self, channel, url,channelType):
        dataList = []
        try:
            soup = self.fetchUrl(url)
            divs = soup.findAll("a",{"class":"card"})
            if len(divs)==0:
                return False
            for ahref in divs:
                if ahref != None:
                    mp4Urls = self.parseDomVideo(ahref.get("href"))
                    if mp4Urls == None or len(mp4Urls)==0:
                        print '没有mp4 文件:', ahref.get("href")
                        continue
                    num = 1
                    for mp4Url in mp4Urls:
                        obj = {}
                        obj['url'] = mp4Url["url"]
                        obj['pic'] = ahref.first("img").get('data-src')
                        #                     item.first('h3').text.replace(" ","")
                        obj['name'] = ahref.first("img").get('alt')+"-"+str(num)
                        num = num + 1
                        print channel, obj['name'],obj['url'],obj['pic']

                        videourl = urlparse(obj['url'])
                        obj['path'] = mp4Url["path"]
                        obj['updateTime'] = datetime.datetime.now()
                        obj['channel'] = channel
                        obj['baseurl'] = baseurl
                        dataList.append(obj)
            dbVPN = db.DbVPN()
            ops = db_ops.DbOps(dbVPN)
            for obj in dataList:
                ops.inertVideo(obj,"normal",baseurl,channelType)

            print 'tv634_ video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
            dbVPN.commit()
            dbVPN.close()
        except Exception as e:
            print common.format_exception(e)
        if len(dataList)==0:
            return False
        return True

    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(url)
            div = soup.first("div", {"class": "ep-grid"})
            if div is None:
                print '没找到播放器div'
                return None
            ahers = div.findAll("a")
            mp4s =[]
            for aherf in ahers:
                item = {}
                item["url"] = aherf.get("href")
                item["path"] = aherf.get("href")
                mp4s.append(item)
                # soupa = self.fetchUrl(aherf.get("href"))
                # script = soupa.first("script", {"id": "playInitialData"})
                # if script!=None:
                #     data = json.loads(script.text)
                #     mp41 = data.get('current', {}).get('src', None)
                #     item = {}
                #     item["url"] = mp41
                #     item["path"] = aherf.get("href")
                #     if mp41!=None:
                #         mp4s.append(item)
            return mp4s
            if murl:
                return murl
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
