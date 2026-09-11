#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from fetch.profile import *
from urllib import unquote
import sys,time,json,re
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
        print '634tv video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            url= item['url']
            channelType = item['channelType']
            
            # 获取最大页码
            # 从第1页遍历到最大页码
            for i in range(1, maxVideoPage):
                    # 页码递减：list_136.html, list_135.html ...
                page_num = i
                page_url = '%s%s%s'%(url.replace('1.html',""), page_num, '.html')
                con = self.videoParse(item['channel'], page_url, channelType)
                if con==False:
                    print '没有数据了 - 页数', i, '---', item['name'], item['url']
                    break
                print '解析完成 ', item['channel'], ' ---', i, '页 / 共'
    
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
            obj['channel']='634tv'+ahref.text
            obj['showType']=3
            obj['channelType']='634tv_all'
            channelList.append(obj)
        # channelList.reverse()
        return  channelList
    def videoParse(self, channel, url,channelType):
        dataList = []
        try:
            soup = self.fetchUrl(url)
            divs = soup.findAll("div",{"class":"stui-vodlist__box"})
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
                    obj['pic'] = baseurl+ahref.get('data-original')
#                     item.first('h3').text.replace(" ","")
                    obj['name'] = ahref.get('title')
                    print channel, obj['name'],obj['url'],obj['pic']

                    videourl = urlparse(obj['url'])
                    obj['path'] = "tv634_"+videourl.path
                    obj['updateTime'] = datetime.datetime.now()
                    obj['channel'] = channel
                    obj['baseurl'] = baseurl
                    dataList.append(obj)
            dbVPN = db.DbVPN()
            ops = db_ops.DbOps(dbVPN)
            for obj in dataList:
                ops.inertVideo(obj,"normal",baseurl,channelType)

            print 'tv634_ video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
            dbVPN.commit()
            dbVPN.close()
        except Exception as e:
            print common.format_exception(e)
        if len(dataList)==0:
            return False
        return True

    def extractM3u8Url(self, text):
        """从播放器页面文本中提取 m3u8 地址，优先解析 player_aaaa JSON"""
        text = unquote(text)
        idx = text.find('var player_aaaa=')
        if idx >= 0:
            json_str = text[idx + len('var player_aaaa='):].strip()
            if json_str.endswith('</script>'):
                json_str = json_str[:json_str.rfind('</script>')].strip()
            data = json.loads(json_str.replace('\\/', '/'))
            murl = data.get('url')
            if murl and 'm3u8' in murl:
                return murl
        match = re.search(r'"url"\s*:\s*"(https?:[^"]+?index\.m3u8)"', text)
        if match:
            return match.group(1).replace('\\/', '/')
        text = text.replace("+@movivecom@+", "stream1.blmwlj.cn")
        for item in text.split(';'):
            match = regVideo.search(item)
            if match is not None:
                return ('http' + match.group(1) + 'm3u8').replace('\\/', '/')
        return None

    def parseDomVideo(self, url):
        try:
            soup = self.fetchUrl(url)
            div = soup.first("div", {"class": "stui-player__video clearfix"})
            if div is None:
                print '没找到播放器div'
                return None
            murl = self.extractM3u8Url(div.text)
            if murl:
                return murl
            print '没找到mp4'
            return None
        except Exception as e:
            print common.format_exception(e)
            return None

def videoParse(queue):
    queue.put(VideoParse())
