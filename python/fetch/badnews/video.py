#!/usr/bin python
# -*- coding: utf-8 -*-
import json

from baseparse import *
from urlparse import urlparse
from common import common
from common import httputil
from fetch.profile import *
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
        print 'rou video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            url= item['url']
            for i in range(1, maxVideoPage):
                con = self.videoParse(item['channel'], item['channelType'],'%s/page-%s'%(url,i))
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
            obj['channel']='badnews_'+ahref.text.replace(" ","")
            obj['showType']=3
            obj['channelType']='badnews_all'
            channelList.append(obj)
        channelList.reverse()
        return  channelList
    def videoParse(self, channel, channelType, url):
        dataList = []
        print "videoParse=", url
        soup = self.fetchUrl(url)
        divs = soup.findAll("div",{"class":"thumbr"})
        if len(divs)==0:
            divs = soup.findAll("div",{"class":"entry "})
            if len(divs)==0:
                divs = soup.findAll("div",{"class":"coverdiv"})
                if len(divs)==0:
                    return False
        for item in divs:
            ahref = item.first('a')
            ddd = item.first('video')
            try:
                if ddd ==None and ahref != None:
                    obj = {}
                    mp4Url = self.parseDomVideo(ahref.get("href"))
                    if mp4Url == None:
                        print '没有mp4 文件:', ahref.get("href")
                        continue
                    obj['url'] = mp4Url
                    imgdiv = ahref.first('img')

                    obj['pic'] = imgdiv.get("data-echo")
    #                     item.first('h3').text.replace(" ","")
                    obj['name'] = self.filter_4byte_chars(imgdiv.get("alt"))
                    obj['path'] = baseurl+ahref.get("href")
                    obj['updateTime'] = datetime.datetime.now()
                    obj['channel'] = channel
                    obj['baseurl'] = baseurl+ahref.get("href")
                    print obj['name'],obj['url'],obj['pic'],obj['baseurl']
                    dataList.append(obj)
                else:
                    ahref = item.first('a',{"class":"dateline"})
                    if ddd != None:
                        obj = {}
                        mp4Url = ddd.get("data-source")
                        if mp4Url == None:
                            print '没有mp4 文件:', ahref.get("href")
                            continue
                        obj['url'] = mp4Url
                        obj['pic'] = ddd.get("poster")
                        h3 = item.first('h3')
                        if h3!=None:
                            obj['name'] = self.filter_4byte_chars(h3.text)
                        else:
                            obj['name'] = '短篇'
                        obj['path'] = baseurl+ahref.get("href")
                        obj['updateTime'] = datetime.datetime.now()
                        obj['channel'] = channel
                        obj['baseurl'] = baseurl+ahref.get("href")
                        print obj['name'],obj['url'],obj['pic'],obj['baseurl']
                        dataList.append(obj)
            except Exception as e:
                print common.format_exception(e)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for i in range(1, 3):
            try:
                for obj in dataList:
                    ops.inertVideo(obj,"normal",baseurl,channelType)
                break
            except Exception as e:
                print common.format_exception(e)
        print 'rou video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        return True
    def filter_4byte_chars(self,text):
        """
        过滤字符串，仅保留：
        - 中文（\u4e00-\u9fa5）
        - 英文（大小写字母 a-zA-Z）
        - 数字（0-9）
        移除所有其他字符
        """
        if not text:
            return u""  # 返回空的Unicode字符串

        # 1. 确保输入为Unicode（处理Python 2.7的str/unicode差异）
        if isinstance(text, str):
            # 尝试用utf-8解码，失败则忽略错误字符
            text = text.decode('utf-8', errors='ignore')
        elif not isinstance(text, unicode):
            return u""  # 非字符串类型直接返回空

        # 2. 正则匹配：只保留中文、英文和数字
        # [\u4e00-\u9fa5] 匹配所有中文字符
        # [a-zA-Z] 匹配所有英文字母（大小写）
        # [0-9] 匹配所有数字
        pattern = re.compile(u'([\u4e00-\u9fa5a-zA-Z0-9])')

        # 3. 提取所有匹配的字符并拼接
        filtered_chars = pattern.findall(text)
        filtered_text = u''.join(filtered_chars)

        return filtered_text
    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(url)
            source = soup.first("video")
            if source != None:
                return source.get("data-source")

            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None