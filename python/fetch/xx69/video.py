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
        print '69xx video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            url= item['url']
            for i in range(1, 4000):
                con = self.videoParse(item['channel'],item['channelType'], '%s%s'%(url,i))
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
            obj['channel']='69xx'+ahref.text
            obj['showType']=3
            obj['channelType']='69xx_all'
            channelList.append(obj)
#         channelList.reverse()
        return  channelList
    def videoParse(self, channel,channelType, url):
        dataList = []
        soup = self.fetchUrl(url)
        divs = soup.findAll("li",{'class':"avdata video-item-col"})
        if len(divs)==0:
            return False
        for item in divs:
            vid = item.get("data-tid")
            if vid != None:
                obj = {}
                mp4Url = self.parseDomVideo('%s%s'%('video/',vid))
                if mp4Url == None:
                    print '没有mp4 文件:', vid
                    continue
                obj['url'] = mp4Url
                imgtext = item.first('img').get('data-src')

                obj['pic'] = imgtext.replace('?ih=1','.webp?ih=1')
#                     item.first('h3').text.replace(" ","")
                obj['name'] = item.first('h3',{'class':'rows-2 f-14 av_data_title'}).text
                print obj['name'],obj['url'],obj['pic']

                videourl = urlparse(obj['url'])
                obj['path'] = "xx69_"+videourl.path
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                obj['baseurl'] = baseurl
                obj['channelType'] = channelType
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,"normal",baseurl)

        print 'xx69 video --解析完毕 ; channel =', channel,';channelType = ',channelType,'; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        return True
    def parseDomVideo(self, url):
        try:
            if url.count("script")==0:
                soup = self.fetchUrl(url)
                source = soup.first("div",{'class':'__player__container ui embed'})
                if source != None:
                    text = source.text.replace(' ','')
                    match = regVideo.search(text)
                    if match!=None:
                        return baseurl+match.group(1)

            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
