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
        print 'kuyunzy video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, maxVideoPage):
                url= item['url']
                if i!=1:
                    url= "%s%s%s"%(item['url'].replace('.html','-'),i,".html")
                self.videoParse(item['channel'], url)
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        soup = self.fetchUrl('/')
        div  = soup.first('div',{'class':'hypoSub clear'})
        channelList =[]
        start = False
        if div!=None:
            ahrefs = div.findAll('a')
            for ahref in ahrefs:
#                 if ahref.text.count('战争片')==0 and start==False:
#                     continue
#                 start = True
                    
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
        lis = soup.findAll("td",{"align":'left'})
        for li in lis:
            ahref = li.first('a')
            if ahref != None:
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                obj['pic'] = ''
                obj['name'] = ahref.text.replace("&nbsp;","")
                obj['path'] = "%s%s%s"%(channel,"-",obj['name'])
                print obj['path'],obj['url'],obj['pic']
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj)

        print 'kuyunzy video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            soup = self.fetchUrl(url, header)
            inputs = soup.findAll("input",{'name':'copy_yah'})
            for input in inputs:
                value = input.get('value')
                if value.count('.m3u8')!=0:
                    return value
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
