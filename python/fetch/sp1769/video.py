#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common


class VideoParse(BaseParse):

    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoChannel(item)
        print '1769 video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            url= item['url'].replace('1.html','')
            for i in range(1, maxPage):
                self.videoParse(item['channel'], (url + "%s.html") % (i))
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        soup = self.fetchUrl('/index.html')
        ul = soup.first('ul',{'class':'f16 menu-list'})
        channelList =[]
        if ul!=None:
            lis = ul.findAll('li',{'class':''})
            for li in lis:
                ahref = li.first('a')
                if ahref!=None:
                    obj={}
                    obj['name']=ahref.text
                    obj['url']=ahref.get('href')
                    obj['baseurl']=baseurl
                    obj['updateTime']=datetime.datetime.now()
                    obj['pic']=''
                    obj['rate']=1.2
                    obj['channel']=ahref.get('href')
                    obj['showType']=3
                    obj['channelType']='normal'
                    channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        lis = soup.findAll("li", {"class": "video "})
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
                obj['pic'] = img.get('src')
                obj['name'] = ahref.get('title')
                print ahref.get('title')

                videourl = urlparse(obj['url'])
                obj['path'] = videourl.path
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj)

        print '1769 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            soup = self.fetchUrl(url, header)
            scripts = soup.findAll("script")
            for s in scripts:
                match = regVideo.search(s.text)
                if match!=None:
                    return match.group(1)+'m3u8'
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
