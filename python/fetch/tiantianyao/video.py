#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
import time,json
from fetch.profile import *
class VideoParse(BaseParse):

    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoChannel(item)
        print '998tiantianyao video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            url = item['url']
            for i in range(1, maxVideoPage):
                if i!=1:
                    url= "/%s%s%s%s"%(item['url'],"index-",i,".htm")
                print url
                self.videoParse(item['channel'], url)
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        ahrefs = self.header()
        channelList = []
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']=obj['name']
            obj['showType']=3
            obj['channelType']='movie'
            channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first("div", {"class": "right"})
        if div!=None:
            uls = div.findAll('div',{"class":"cl"})
            for ul in uls:
                obj = {}
                ahref = ul.first('a')
                if ahref!=None:
                    mp4Url = self.parseDomVideo(ahref.get("href"))
                    if mp4Url == None:
                        print '没有mp4 文件:', ahref.get("href")
                        continue
                    obj['url'] = mp4Url
                    img = ahref.first('img')
                    obj['pic'] = img.get("src")
                    obj['name'] = img.get('alt').replace("点击播放","").replace("《","").replace("》","")
                    if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                        obj['videoType'] = "webview"
                    else:
                        obj['videoType'] = "normal"
                    obj['baseurl'] = baseurl
                    videourl = urlparse(obj['url'])
                    obj['path'] = videourl.path
                    obj['updateTime'] = datetime.datetime.now()
                    if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                        obj['videoType'] = "webview"
                    else:
                        obj['videoType'] = "normal"
                    obj['channel'] = channel
                    obj['baseurl'] = baseurl
                    print obj['videoType'],obj['url'],obj['pic']
                    dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,obj['videoType'],baseurl)

        print '998tiantianyao video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            soup = self.fetchUrl(url, header)
            div = soup.first("div",{'class':'playurl'})
            if div!=None:
                ahref = div.first('a')
                if ahref!=None:
                    soup = self.fetchUrl(ahref.get('href'), header)
                    play_video = soup.first('div',{'class':'player'})
                    if play_video!=None:
                        script = play_video.first('script')
                        if script!=None:
                            content = unquote(str(script.text))
                            match = regVideo.search(content)
                            if match!=None:
                                obj = json.loads(match.group(1))
                                data = obj.get('Data',[])
                                urlData = []
                                for item in data:
                                    itemData = item.get('playurls',[])
                                    for itemUrl in itemData:
                                        for itemurlOne in itemUrl:
                                            if itemurlOne.count('http')>0:
                                                urlData.append(itemurlOne)
                                for item in urlData:
                                    if item.count('m3u8'):
                                        return item
                                for item in urlData:
                                    if item.count('/share/'):
                                        return item
                                if len(urlData)>0:
                                    return urlData[0]
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
