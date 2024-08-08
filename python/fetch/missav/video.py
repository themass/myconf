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
        print 'missav video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            url= item['url']
            for i in range(800, maxVideoPage):
                con = self.videoParse(item['channel'], item['channelType'],'%s?page=%s'%(url,i))
                if con==False:
                    print '没有数据了啊-======页数',i,'---',item['name'],item['url']
                    break
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def videoChannel(self):
        channelList = []
        ahrefs = self.header(name="header.html")
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']='missav'+ahref.text
            obj['showType']=3
            obj['channelType']='missav_all'
            channelList.append(obj)
#         channelList.reverse()
        return  channelList
    def videoParse(self, channel, channelType, url):
        dataList = []
        soup = self.fetchUrlWithBase(url)
        divs = soup.findAll("div",{"class":"relative aspect-w-16 aspect-h-9 rounded overflow-hidden shadow-lg"})
        if len(divs)==0:
            return False
        for item in divs:
            ahref = item.first('a')
            if ahref != None:
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                imgdiv = ahref.first('img')
                obj['pic'] = imgdiv.get("data-src")
#                     item.first('h3').text.replace(" ","")
                obj['name'] = imgdiv.get("alt")
                videourl = urlparse(obj['url'])
                obj['path'] = ahref.get("href")
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                obj['baseurl'] = ahref.get("href")
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
        print 'missav video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
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
def videoParse(queue):
    queue.put(VideoParse())
