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
        print '17ishare video -- channel ok;,len=',len(chs)
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
        channelList=[]
        obj={}
        obj['name']='剧情2'
        obj['url']="/vodtypehtml/1.html"
        obj['baseurl']=baseurl
        obj['updateTime']=datetime.datetime.now()
        obj['pic']=''
        obj['rate']=1.2
        obj['channel']=baseurl.replace("http://", "").replace("https://", "")+'/vodtypehtml/1.html';
        obj['showType']=3
        obj['channelType']='movie'
        channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        lis = soup.findAll("div",{"class":'movie-item'})
        for li in lis:
            ahref = li.first('a')
            if ahref != None:
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                img = li.first("img")
                obj['pic'] = baseurl+img.get('src')
                obj['name'] = img.get('title')
                print img.get('title')

                videourl = urlparse(obj['url'])
                obj['path'] = videourl.path
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                obj['baseurl'] = baseurl
                dataList.append(obj)
            dbVPN = db.DbVPN()
            ops = db_ops.DbOps(dbVPN)
            for obj in dataList:
                ops.inertVideo(obj,"normal",baseurl)
    
            print 'ir6y video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
            dbVPN.commit()
            dbVPN.close()
            time.sleep(5)

    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        videos = []
        try:
            soup = self.fetchUrl(url, header)
            divs = soup.findAll("div",{'class':'panel panel-default resource-list ptab ptabw'})
            for div in divs:
                span = div.first('span')
                if span!=None:
                    if span.text('手机')!=0:
                        ahrefs = soup.findAll('a')
                        for ahref in ahrefs:
                            soup = self.fetchUrl(ahref.get('href'), header)
                            movieid = soup.first('td',{"class":"movieid"})
                            script = movieid.first('script')
                            content = self.fetchContentUrlWithBase(script.get("src"),header)
                            content = unquote(str(content))
            print '没找到mp4'
            return videos
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
