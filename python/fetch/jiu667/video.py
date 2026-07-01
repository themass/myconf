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
        print 'jiu667 video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            url= item['url']
            channelType = item['channelType']
            
            # 获取最大页码
            max_page = self.get_max_page(url)
            if max_page == 0:
                print '无法获取最大页码:', url
                continue
            
            print '频道:', item['channel'], '最大页码:', max_page
            
            # 从第1页遍历到最大页码
            for i in range(1, max_page + 1):
                con = False
                if i==1:
                    con = self.videoParse(item['channel'], url, channelType)
                else:
                    # 页码递减：list_136.html, list_135.html ...
                    page_num = max_page - i + 2
                    page_url = '%s%s%s'%(url.replace('index.html','list_'), page_num, '.html')
                    con = self.videoParse(item['channel'], page_url, channelType)
                
                if con==False:
                    print '没有数据了 - 页数', i, '---', item['name'], item['url']
                    break
                print '解析完成 ', item['channel'], ' ---', i, '页 / 共', max_page, '页'
    
    def get_max_page(self, url):
        """
        获取最大页码
        从分页导航中提取最大的页码数字
        """
        try:
            soup = self.fetchUrl(url)
            pagination = soup.first('div', {"class": "pagination"})
            if pagination != None:
                # 查找所有 a 标签中的页码
                links = pagination.findAll('a')
                max_page = 0
                for link in links:
                    href = link.get('href', '')
                    # 匹配 list_数字.html 格式
                    import re
                    match = re.search(r'list_(\d+)\.html', href)
                    if match:
                        page_num = int(match.group(1))
                        if page_num > max_page:
                            max_page = page_num
                return max_page
            return 0
        except Exception as e:
            print '获取最大页码失败:', common.format_exception(e)
            return 0
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
            obj['channel']='jiu667'+ahref.text
            obj['showType']=3
            obj['channelType']='jiu667_all'
            channelList.append(obj)
        # channelList.reverse()
        return  channelList
    def videoParse(self, channel, url,channelType):
        dataList = []
        try:
            soup = self.fetchUrl(url)
            div = soup.first('ul',{"class":"row col5 clearfix"})
            if div!=None:
                divs = div.findAll("li")
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
                        img = ahref.first('img')
                        obj['pic'] = baseurl+img.get('data-original')
    #                     item.first('h3').text.replace(" ","")
                        obj['name'] = ahref.get('title')
                        print channel, obj['name'],obj['url'],obj['pic']

                        videourl = urlparse(obj['url'])
                        obj['path'] = "jiu667_"+videourl.path
                        obj['updateTime'] = datetime.datetime.now()
                        obj['channel'] = channel
                        obj['baseurl'] = baseurl
                        dataList.append(obj)
            dbVPN = db.DbVPN()
            ops = db_ops.DbOps(dbVPN)
            for obj in dataList:
                ops.inertVideo(obj,"normal",baseurl,channelType)

            print 'jiu667 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
            dbVPN.commit()
            dbVPN.close()
        except Exception as e:
            print common.format_exception(e)
        if len(dataList)==0:
            return False
        return True

    def parseDomVideo(self, url):
        try:
            if url.count("script")==0:
                soup = self.fetchUrl(url)
                scripts = soup.findAll("script")
                for s in scripts:
                    text = unquote(s.text).replace("+@movivecom@+","watch1.kiveht.com")
                    texts = text.split(';')
                    for item in texts:
                        match = regVideo.search(item)
                        if match!=None:
                            return 'http'+match.group(1)+'m3u8'
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
