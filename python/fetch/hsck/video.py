#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from fetch.profile import *
from urllib import unquote
import sys,time,json,urllib2
reload(sys)
# 
sys.setdefaultencoding('utf8')

class VideoParse(BaseParse):
    names = ''
    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoChannel(item)
        print 'hsck video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            url= item['url']
            for i in range(1, maxVideoPage):
                con = self.videoParse(item['channel'], item['channelType'],'%s%s.html'%(url.replace(".html","/page/"),i))
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
            obj['channel']='hsck'+ahref.text
            obj['showType']=3
            obj['channelType']='hsck_all'
            channelList.append(obj)
        channelList.reverse()
        return  channelList
    def videoParse(self, channel, channelType, url):
        dataList = []
        soup = self.fetchUrl(url)
        divs = soup.findAll("div",{"class":"stui-vodlist__box"})
        nameTemp = ''
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
                obj['pic'] = ahref.get('data-original')
                obj['name'] = ahref.get("title")

                obj['path'] = 'hsck'+ahref.get("href")
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                obj['baseurl'] = baseurl+ahref.get("href")
                print obj['name'],obj['url'],obj['pic'],obj['baseurl']
                dataList.append(obj)
                nameTemp= nameTemp+obj['name']
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for i in range(1, 3):
            try:
                for obj in dataList:
                    ops.inertVideo(obj,"normal",baseurl,channelType)
                break
            except Exception as e:
                print common.format_exception(e)
        print 'hsck video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        if nameTemp == self.names:
            print nameTemp
            return False
        else:
            self.names = nameTemp
        return True
    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(url)
            # source = soup.first("source",{'id':'mp4m3u8'})
            source = soup.first("div",{'class':'stui-player__video clearfix'})
            if source != None:
                print source.text
                data = json.loads(source.text.replace("var player_aaaa=","").replace("\/","/"))
                murl = data.get("url",None)
                
                # 验证 URL 是否有效
                if murl and self.check_url_valid(murl):
                    return murl
                else:
                    return None

            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None
    
    def check_url_valid(self, url):
        """
        检查 URL 是否有效，只有返回 200 状态码才认为有效
        """
        try:
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36')
            response = urllib2.urlopen(req, timeout=5)
            code = response.getcode()
            if code == 200:
                return True
            else:
                print 'URL 无效:', url, '状态码:', code
                return False
        except Exception as e:
            print 'URL 访问失败:', url, '错误:', str(e)
            return False

def videoParse(queue):
    queue.put(VideoParse())
