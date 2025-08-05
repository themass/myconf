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
        print 'hsex video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            url= item['url']
            for i in range(1, maxVideoPage):
                con = self.videoParse(item['channel'], item['channelType'],'%s%s'%(url,i))
                if con==False:
                    print '没有数据了啊-======页数',i,'---',item['name'],item['url']
                    break
                print '解析完成 ', item['channel'], ' ---', i, '页'
    def runUrls(self):
        for url in urls:
            for i in range(1, 100):
                page = '%s/%s'%(url,i)
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
            obj['channel']='hsex'+ahref.text
            obj['showType']=3
            obj['channelType']='weav_all'
            channelList.append(obj)
#         channelList.reverse()
        return  channelList
    def videoParse(self, channel, channelType, url):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first('div',{"class":"video-av-data"})

        if div!=None:
            divs = div.findAll("div",{"class":"avdata-outer col-3"})
            if len(divs)==0:
                return False
            for item in divs:
                ahref = item.first('a')
                if ahref != None:
                    obj = {}
                    mp4Url = self.extract_hash_id(ahref.get("href"))
                    if mp4Url == None:
                        print '没有mp4 文件:', ahref.get("href")
                        continue
                    obj['url'] = mp4Url
                    imgdiv = ahref.first('img')

                    obj['pic'] = imgdiv.get("data-src")
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
        time.sleep(1)
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
    def extract_hash_id(self, url):
        """
        从文本中提取 hash_id 的值

        参数:
            text (str): 包含 hash_id 的原始文本
        返回:
            str: 匹配到的 hash_id 值，如果未找到则返回 None
        """
        # 正则表达式模式：匹配 "hash_id":"任意字符" 的结构
        # 其中 .*? 表示非贪婪匹配任意字符（除换行外），确保只匹配到第一个双引号结束
        text = self.fetchContent(url)
        pattern = r'"hash_id":"(.*?)"'

        # 使用 re.search 查找第一个匹配项
        match = re.search(pattern, text)

        # 如果找到匹配，返回捕获组中的内容（即 hash_id 的值）
        if match:
            return "https://b2.bttss.cc/videos/"+match.group(1)+"/g.m3u8"
        else:
            return None
def videoParse(queue):
    queue.put(VideoParse())
