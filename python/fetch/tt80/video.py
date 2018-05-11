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
                    url= "/%s%s%s"%(item['url'].replace(".html","-"),i,".html")
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
        div = soup.first("div", {"class": "channel"})
        uls = div.findAll('li')
        for ul in uls:
            ahref = ul.first('a')
            if ahref!=None:
                mp4Urls = self.parseDomVideo(ahref.get("href"))
                if len(mp4Urls)==0:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                index = 1
                for mp4Url in mp4Urls:
                    obj = {}
                    obj['url'] = mp4Url
                    img = ahref.first('img')
                    obj['pic'] = img.get("data-original")
                    obj['name'] = img.get('alt').replace("点击播放","").replace("《","").replace("》","")+str(index)
                    if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                        obj['videoType'] = "webview"
                    else:
                        obj['videoType'] = "normal"
                    index = index+1
                    videourl = urlparse(obj['url'])
                    obj['path'] = videourl.path
                    obj['updateTime'] = datetime.datetime.now()
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
        header = {"Cookie":"UM_distinctid=1634dc359232a8-0bb5fc4253d1fa-454c092b-1fa400-1634dc359262b6; PHPSESSID=bsmjidrh538n8g1tdgma49d5b4; CNZZDATA1263540662=1817384014-1526013810-null%7C1526060398; mac_history=%7Bvideo%3A%5B%7B%22name%22%3A%22%u5934%u53F7%u73A9%u5BB6%22%2C%22link%22%3A%22/dv/14210/14210.html%22%2C%22typename%22%3A%22%u79D1%u5E7B%u7247%22%2C%22typelink%22%3A%22/dv/-pg-1.html%22%2C%22pic%22%3A%22http%3A//img1.doubanio.com/view/photo/s_ratio_poster/public/p2516578307.jpg%22%7D%2C%7B%22name%22%3A%22%u7F8E%u8DB3%u7F8E%u5973%u89C6%u989120180509%20%5B11%5D%22%2C%22link%22%3A%22/dv/15880/15880.html%22%2C%22typename%22%3A%22%u798F%u5229%u89C6%u9891%22%2C%22typelink%22%3A%22/dv/-pg-1.html%22%2C%22pic%22%3A%22https%3A//156zy.suyunbo.tv/2018/05/10/OcQt8szOetreqzP1/screenshot1.jpg%22%7D%2C%7B%22name%22%3A%22%u7F6A%u4EBA%u4E0E%u9F99%u5171%u821E%22%2C%22link%22%3A%22/dv/15959/15959.html%22%2C%22typename%22%3A%22%u52A8%u6F2B%22%2C%22typelink%22%3A%22/dv/-pg-1.html%22%2C%22pic%22%3A%22http%3A//img3.doubanio.com/view/photo/s_ratio_poster/public/p2516380082.jpg%22%7D%2C%7B%22name%22%3A%22%u8D85%u80FD%u529B%u8005%22%2C%22link%22%3A%22/dv/8319/8319.html%22%2C%22typename%22%3A%22%u79D1%u5E7B%u7247%22%2C%22typelink%22%3A%22/dv/-pg-1.html%22%2C%22pic%22%3A%22http%3A//p6.qhimg.com/d/dy_4a648e5fbf851bbb569686b63b725ce3.jpg%22%7D%2C%7B%22name%22%3A%22%u7FA4%u9E1F%u4E4B%u5730%22%2C%22link%22%3A%22/dv/15951/15951.html%22%2C%22typename%22%3A%22%u5267%u60C5%u7247%22%2C%22typelink%22%3A%22/dv/-pg-1.html%22%2C%22pic%22%3A%22http%3A//img3.doubanio.com/view/photo/s_ratio_poster/public/p2518129996.jpg%22%7D%2C%7B%22name%22%3A%22%u7F8E%u8DB3%u7F8E%u5973%u89C6%u989120180510%20%5B1%5D%22%2C%22link%22%3A%22/dv/15943/15943.html%22%2C%22typename%22%3A%22%u798F%u5229%u89C6%u9891%22%2C%22typelink%22%3A%22/dv/-pg-1.html%22%2C%22pic%22%3A%22https%3A//156zy.suyunbo.tv/2018/05/11/5fVQnezSjpep3uzG/screenshot1.jpg%22%7D%2C%7B%22name%22%3A%22%u63BA%u5047%u65F6%u4EE3%22%2C%22link%22%3A%22/dv/15856/15856.html%22%2C%22typename%22%3A%22%u4F26%u7406%u7535%u5F71%22%2C%22typelink%22%3A%22/dv/-pg-1.html%22%2C%22pic%22%3A%22http%3A//ww1.sinaimg.cn/large/006K6oEIgy1fr5fm10vobj3068095wh0.jpg%22%7D%2C%7B%22name%22%3A%22%u597D%u5973%u5B69%22%2C%22link%22%3A%22/dv/2386/2386.html%22%2C%22typename%22%3A%22%u4F26%u7406%u7535%u5F71%22%2C%22typelink%22%3A%22/dv/-pg-1.html%22%2C%22pic%22%3A%22http%3A//img3.doubanio.com/view/movie_poster_cover/lpst/public/p2480898061.jpg%22%7D%2C%7B%22name%22%3A%22%u7F8E%u8DB3%u7F8E%u5973%u89C6%u989120180509%20%5B13%5D%22%2C%22link%22%3A%22/dv/15882/15882.html%22%2C%22typename%22%3A%22%u798F%u5229%u89C6%u9891%22%2C%22typelink%22%3A%22/dv/-pg-1.html%22%2C%22pic%22%3A%22https%3A//156zy.suyunbo.tv/2018/05/10/XFxghJelyOibTiLt/screenshot1.jpg%22%7D%2C%7B%22name%22%3A%22%u6FC0%u6218%u67CF%u6797%22%2C%22link%22%3A%22/dv/2667/2667.html%22%2C%22typename%22%3A%22%u4F26%u7406%u7535%u5F71%22%2C%22typelink%22%3A%22/dv/-pg-1.html%22%2C%22pic%22%3A%22http%3A//img1.doubanio.com/view/movie_poster_cover/lpst/public/p2389656488.jpg%22%7D%5D%7D; yunsuo_session_verify=66f53834bfa109844cac87609cd3e8d2; yunsuo_leech_key=36","Upgrade-Insecure-Requests":1,'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            soup = self.fetchUrl(url, header)
            div = soup.first("div",{'class':'playlist'})
            mp4Urls = []
            mp4Urlsm3 = []
            mp4Urlsshare = []
            if div!=None:
                ahref = div.first('a')
                if ahref!=None:
                    soup = self.fetchUrl(ahref.get('href'), header)
                    play_video = soup.first('div',{'class':'player'})
                    if play_video!=None:
                        script = play_video.first('script')
                        if script!=None:
                            content = self.fetchContentUrl(script.get('src'), header)
                            contents = unquote(str(content)).replace("#", "$").replace("');", "").split("$")
                            for item in contents:
                                match = regVideo.search(item)
                                if match!=None:
                                    mp4Urlsm3.append("%s%s%s"%("http",match.group(1),"m3u8"))
                            for item in contents:
                                if item.count(regVideoyun)>0:
                                    mp4Urlsshare.append(item)
                                    continue
                            if len(mp4Urlsm3)>0:
#                                 mp4Urls.extend(mp4Urlsm3)
                                return mp4Urls
                            else:
                                mp4Urls.extend(mp4Urlsshare)
            return mp4Urls
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
