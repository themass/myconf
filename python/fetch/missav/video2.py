#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
import time
from fetch.profile import *
class VideoUserParse(BaseParse):

    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            print item
            ops.inertVideoUser(item)
        print 'missav user video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            for i in range(1, 1000):
                url= "%s%s%s"%(item['url'],"?page=",i)
                print url
                con = self.videoParse(item['channel'], url,item['userId'])
                print '解析完成 ', item['channel'], ' ---', i, '页'
                if con==False:
                    print '没有数据了啊-======页数',i,'---',item['name'],item['url']
                    break
    def videoChannel(self):
        channelList = []

        ahrefs = self.header(name="header2.html")
        for ahref in ahrefs:
            for i in range(1000, 1200):
                url= '%s?page=%s'%(ahref.get("href"),i)
                print '开始下载',url
                soup = self.fetchUrl(url)
                ul = soup.first("ul",{"class":"mx-auto grid grid-cols-2 gap-4 gap-y-8 sm:grid-cols-4 md:gap-6 lg:gap-8 lg:gap-y-12 xl:grid-cols-6 text-center"})
                lis =  ul.findAll("li")
                count = 0
                for item in lis:
                    print i
                    if i==5:
                        if count <8 :
                            count = count+1
                            print '忽略',i ,count
                            continue
                    div = item.first("div",{"class":"space-y-4"})
                    obj={}
                    obj['name']=div.first("h4").text
                    obj['url']=div.first("a").get('href')
                    obj['baseUrl']=baseurl
                    obj['updateTime']=datetime.datetime.now()
                    if div.first("img")!=None:
                        obj['pic']= div.first("img").get("src")
                    else:
                        obj['pic']=''
                    obj['rate']=1.2
                    obj['channel']='missav女优一览'
                    obj['userId']="missav"+obj['name']
                    obj['showType']=3
                    obj['channelType']='normal'
                    print obj['name']
                    channelList.append(obj)
                print '下载ok', url
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrlWithBase(url)
        divs = soup.findAll("div",{"class":"relative aspect-w-16 aspect-h-9 rounded overflow-hidden shadow-lg"})
        if len(divs)==0:
            return False
        for item in divs:
            #name,pic,url,userId,rate,updateTime,path
            ahref = item.first('a')
            if ahref!=None:
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                imgdiv = ahref.first('img')
                obj['pic'] = imgdiv.get("data-src")
                obj['name'] = imgdiv.get("alt")
    
                videourl = urlparse(obj['url'])
                obj['path'] = userId+videourl.path
                obj['rate'] = 1.2
                obj['updateTime'] = datetime.datetime.now()
                obj['userId'] = userId
                obj['baseUrl'] = baseurl
                obj['showType'] = 3
                obj['channel'] = channel
                if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                    obj['videoType'] = "webview"
                else:
                    obj['videoType'] = "normal"
                print obj['videoType'],obj['name'],mp4Url,obj['pic']
                dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideoUserItem(obj)

        print 'missav video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        if len(dataList)==0:
            return False
        return True

    def parseDomVideo(self, url):
        try:
            data = httputil.getText(url,header = header,isGzip=True)
            return parserText(data)
        except Exception as e:
            print common.format_exception(e)
            return None
def js_to_python(p, a, c, k, e, d):
    for i in range(c - 1, -1, -1):
        if k[i]:
            p = re.sub(r"\b" + int_to_base36(i) + r"\b", k[i], p)
    return p

def int_to_base36(num):
    # Convert a number to base 36 as a string
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    base36 = ""
    while num:
        num, i = divmod(num, 36)
        base36 = chars[i] + base36
    return base36 or '0'
def parserText(text):
    match = re.search(r"eval\(function\(p,a,c,k,e,d\)\{.*?\}\('(.*?)',(\d+),(\d+),'(.*?)'\.split\('\|'\),(\d+),\{\}\)\)", text)
    if match:
        p = match.group(1)
        a = int(match.group(2))
        c = int(match.group(3))
        k = match.group(4).split('|')
        e = int(match.group(5))
        d = {}
        decoded_code = js_to_python(p, a, c, k, e, d)
        liststr = decoded_code.split(";")
        for item in liststr:
            match = regVideo.search(item)
            if match!=None:
                videoUrl =match.group(1)
                return "%s%s%s"%("http",videoUrl,'m3u8')
    return None
