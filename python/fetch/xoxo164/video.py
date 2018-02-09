#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
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
        print 'xoxo164 video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        start=1
        for item in chs:
#             if start<=4:
#                 start=start+1
#                 continue
            print item['name']
            url= item['url'].replace('/1/','')
            for i in range(1, maxVideoPage):
                self.videoParse(item['channel'], (url + "/%s/") % (i))
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        soup = self.fetchUrl('/')
        uls = soup.findAll('ul',{'class':'nav_menu clearfix'})
        print uls
        channelList =[]
        for ul in uls:
            ul.first('li',{'class':'active'})
            print ul.text
            if ul!=None :
                a = ul.first('a')
                if a!=None and (a.text=='视频二区'):
                    ahrefs = ul.findAll('a')
                    for ahref in ahrefs:
                        if ahref.get('href')!='/':
                                obj={}
                                obj['name']=ahref.text
                                obj['url']=ahref.get('href')
                                obj['baseurl']=baseurl
                                obj['updateTime']=datetime.datetime.now()
                                obj['pic']=''
                                obj['rate']=1.2
                                obj['channel']=baseurl.replace("http://", "").replace("https://", "")+ahref.get('href')
                                obj['showType']=3
                                obj['channelType']='normal'
                                channelList.append(obj)
        return channelList
    def videoParse(self, channel, url):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first("div", {"class": "box movie_list"})
        if div!=None:
            ahrefs = div.findAll('a')
            print ahrefs
            for ahref in ahrefs:
                if ahref.get('href')!='/':
                    obj = {}
                    mp4Url = self.parseDomVideo(ahref.get("href"))
                    if mp4Url == None:
                        print '没有mp4 文件:', ahref.get("href")
                        continue
                    obj['url'] = mp4Url
                    img = ahref.first("img")
                    obj['pic'] = img.get('src')
                    obj['name'] = ahref.first('h3').text
                    print obj['name'],mp4Url
    
                    videourl = urlparse(obj['url'])
                    obj['path'] = videourl.path
                    obj['updateTime'] = datetime.datetime.now()
                    obj['channel'] = channel
                    dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj)

        print 'xoxo164 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()

    def parseDomVideo(self, url):
        header = {'User-Agent':
                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": url}
        try:
            soup = self.fetchUrl(url, header)
            div = soup.first("div",{'class':'film_bar clearfix'})
            if div!=None:
                ahref = div.first('a')
                if ahref!=None:
                    soup = self.fetchUrl(ahref.get('href'), header)
                    play = soup.first('div',{'class':'player_l'})
                    if play!=None:
                        script = play.first('script')
                        if script!=None:
                            match = regVideo.search(script.text)
                            if match!=None :
                                return unquote(match.group(2)+match.group(3))
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None
        
def videoParse(queue):
    queue.put(VideoParse())
