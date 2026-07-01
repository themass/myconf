#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from fetch.profile import *
from urllib import unquote
import sys,time,json,re,urllib2
import threading
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
        print 'xiaoyakankan video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            url= item['url']
            for i in range(1, maxVideoPage):
                con = self.videoParse(item['channel'], item['channelType'],'%s%s%s'%(url.replace('.html','-'),i,'.html'))
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
            obj['channel']='xiaoyakankan'+ahref.text
            obj['showType']=3
            obj['channelType']='xiaoyakankan_all'
            channelList.append(obj)
#         channelList.reverse()
        return  channelList
    def videoParse(self, channel, channelType, url):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first('div',{"class":"m4-list"})
        if div!=None:
            divs = div.findAll("div",{"class":"item"})
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
                    obj['pic'] = '%s%s'%("https:", item.first('img').get('data-src'))
                    obj['name'] = item.first('img').get("alt")

                    obj['path'] = 'xiaoya'+ahref.get("href")
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
        print 'xiaoyakankan video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        if len(dataList) ==0:
            return False
        return True
    def parseDomVideo(self, url):
        """
        解析视频页面，提取 m3u8 链接
        优先级:
        1. hd.ijycnd.com
        2. play.maoyanplay.top
        3. 其他线路：从前往后选择，取第1项（index 0）
        """
        try:
            soup = self.fetchUrl(url)
            scripts = soup.findAll("script")
            
            all_lines = []  # 存储所有解析到的线路
            
            for script in scripts:
                text = script.text
                if not text:
                    continue
                
                # 检查是否包含 var pp=
                if 'var pp=' not in text:
                    continue
                
                # 提取 JSON 部分
                # 匹配 var pp={...};
                match_json = re.search(r'var\s+pp\s*=\s*(\{.*?\});', text, re.DOTALL)
                if not match_json:
                    continue
                
                json_str = match_json.group(1)
                try:
                    data = json.loads(json_str)
                    lines = data.get('lines', [])
                    
                    # 遍历所有线路
                    for line_item in lines:
                        # line_item 结构: ["id", "name", status, [url]]
                        if len(line_item) < 4:
                            continue
                        
                        urls = line_item[3]
                        if not urls or len(urls) == 0:
                            continue
                        
                        m3u8_url = urls[0]  # 取第一个 URL
                        
                        # 统一处理 URL 格式
                        if m3u8_url.startswith('//'):
                            m3u8_url = 'https:' + m3u8_url
                        elif not m3u8_url.startswith('http'):
                            continue  # 跳过非标准 URL
                        
                        # 忽略包含 svip 的域名
                        if 'svip' in m3u8_url.lower():
                            continue
                        
                        # 忽略包含 jpzy01 的域名
                        if 'jpzy01' in m3u8_url.lower():
                            continue
                        
                        # 忽略包含 v14 的域名
                        if 'v14' in m3u8_url.lower():
                            continue
                        
                        # 忽略包含 vod12 的域名
                        if 'vod12' in m3u8_url.lower():
                            continue
                        
                        # 忽略包含 kuaichezym3u8 的域名
                        if 'kuaichezym3u8' in m3u8_url.lower():
                            continue
                        
                        # 忽略包含 bfllvip 的域名
                        if 'bfllvip' in m3u8_url.lower():
                            continue
                        
                        # 忽略包含 qsstvw 的域名
                        if 'qsstvw' in m3u8_url.lower():
                            continue
                        
                        # 忽略包含 phimgood 的域名
                        if 'phimgood' in m3u8_url.lower():
                            continue
                        
                        # 忽略包含 gghijk 的域名
                        if 'gghijk' in m3u8_url.lower():
                            continue
                        
                        # 忽略包含 v13 的域名
                        if 'v13' in m3u8_url.lower():
                            continue
                        
                        # HTTP 访问验证：只保留返回 200 的 URL
                        if not self.check_url_valid(m3u8_url):
                            continue
                        
                        all_lines.append(m3u8_url)
                        
                        # 优先级 1: hd.ijycnd.com - 立即返回
                        if 'hd.ijycnd.com' in m3u8_url:
                            return m3u8_url
                            
                except Exception as e:
                    print "JSON Parse Error:", common.format_exception(e)
                    continue
            
            # 如果没有找到优先级1的，查找优先级2: play.maoyanplay.top
            for u in all_lines:
                if 'play.maoyanplay.top' in u:
                    return u
            
            # 优先级 3: 从前往后选择，取第1项（index 0）
            if len(all_lines) > 0:
                return all_lines[0]

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
