#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlall import *
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
        print 'j18 video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            url= item['url']
            for i in range(1, maxVideoPage):
                con = self.videoParse(item['channel'], item['channelType'],'%s-%s/'%(url,i))
                if con==False:
                    print '没有数据了啊-======页数',i,'---',item['name'],item['url']
                    break
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def runUrls(self):
        for url in urls:
            for i in range(1, 100):
                page = url%(i)
                con = self.videoParse('weav', 'weav_all',page)
                if con==False:
                    print '没有数据了啊-======页数',i,'---',page
                    break
                print '解析完成 ', url, ' ---', i, '页'
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
            obj['channel']='j18'+ahref.text
            obj['showType']=3
            obj['channelType']='weav_all'
            channelList.append(obj)
#         channelList.reverse()
        return  channelList
    def videoParse(self, channel, channelType, url):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first('ul',{"class":"list"})

        if div!=None:
            divs = div.findAll("li")
            if len(divs)==0:
                return False
            for item in divs:
                ahref = item.first('a')
                if ahref != None:
                    obj = {}
                    mp4Url = self.findM3u8Url(ahref.get("href"))
                    if mp4Url == None:
                        print '没有mp4 文件:', ahref.get("href")
                        continue
                    obj['url'] = mp4Url
                    imgdiv = ahref.first('img')

                    obj['pic'] = imgdiv.get("data-original")
#                     item.first('h3').text.replace(" ","")
                    obj['name'] = imgdiv.get("alt")
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
        print 'hsex video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        time.sleep(1)
        return True
    def parseDomVideo(self, url):
        try:
            if url.count("script")==0:
                soup = self.fetchUrl(url)
                source = soup.first("source")
                if source != None:
                    text = source.get("src")
                    return text

            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None
    def findM3u8Url(self, url):
        try:
            text = self.fetchContent( url)
            pattern = r"const source = '([^']+\.m3u8)'"
            match = re.search(pattern, text)
            if match:
                return match.group(1)
            else:
                print "未找到 m3u8 链接",url
                return None
        except Exception as e:
            print common.format_exception(e)
            return None
def videoParse(queue):
    queue.put(VideoParse())
