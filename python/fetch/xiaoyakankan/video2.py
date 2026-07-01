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
        ahrefs = self.header2()
        for ahref in ahrefs:
            obj={}
            obj['name']=ahref.text
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']=ahref.text
            obj['showType']=3
            obj['channelType']='movie'
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
                        
                        all_lines.append(m3u8_url)
                            
                except Exception as e:
                    print "JSON Parse Error:", common.format_exception(e)
                    continue
            
            if not all_lines:
                print '没找到mp4'
                return None
            
            # 并行访问所有 URL，返回第一个 200 的
            result = self.check_urls_parallel(all_lines)
            if result:
                return result
            
            print '没找到有效的mp4'
            return None

        except Exception as e:
            print common.format_exception(e)
            return None
    
    def check_urls_parallel(self, urls):
        """
        并行访问多个 URL，返回第一个返回 200 状态码的 URL
        """
        import Queue
        result_queue = Queue.Queue()
        threads = []
        
        def check_single_url(url):
            """检查单个 URL 的有效性"""
            try:
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36')
                response = urllib2.urlopen(req, timeout=5)
                code = response.getcode()
                if code == 200:
                    result_queue.put(url)
            except Exception as e:
                pass  # 忽略失败的 URL
        
        # 创建并启动所有线程
        for url in urls:
            t = threading.Thread(target=check_single_url, args=(url,))
            t.daemon = True
            threads.append(t)
            t.start()
        
        # 等待第一个有效结果
        try:
            valid_url = result_queue.get(timeout=8)  # 最多等待 8 秒
            print '找到有效URL:', valid_url
            return valid_url
        except:
            return None

def videoParse(queue):
    queue.put(VideoParse())
