#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from fetch.profile import *
from urllib import unquote
import sys,time
import base64
reload(sys)
# 
sys.setdefaultencoding('utf8')

class VideoParse(BaseParse):

    def __init__(self):
        BaseParse.__init__(self)  # 初始化基础解析类
        threading.Thread.__init__(self)  # 初始化线程类
        self.baseurl = baseurl
        # 模拟浏览器 headers，减少被拒绝概率
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }
        self.max_retries = maxCount
        # 自定义SSL上下文（进一步放宽限制）
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
        # 允许较旧的SSL/TLS协议（应对服务器协议兼容问题）
        self.ctx.options |= ssl.OP_NO_SSLv2
        self.ctx.options |= ssl.OP_NO_SSLv3
        # 可选：根据服务器支持的协议调整（如允许TLSv1.0/1.1）
        # self.ctx.options &= ~ssl.OP_NO_TLSv1
        # self.ctx.options &= ~ssl.OP_NO_TLSv1_1
        # 初始化SSL上下文（修复兼容性问题）
        self._init_ssl_context()

        # 模拟浏览器请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.google.com/'
        }

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoChannel(item)
        print 'mzford video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            url= item['url']
            channelType = item['channelType']
            for i in range(1, maxVideoPage):
                try:
                    con = False
                    if i==1:
                        con = self.videoParse(item['channel'], '%s%s'%(url,"/index.html"),channelType)
                    else:
                        con = self.videoParse(item['channel'], '%s%s%s%s'%(url,'/index_',i,'.html'),channelType)
                    if con==False:
                        print '没有数据了啊-======页数',i,'---',item['name'],item['url']
                        break
                    print '解析完成 ', item['channel'], ' ---', i, '页'
                except Exception as e:
                    pass
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
            obj['channel']='c4441'+ahref.text
            obj['showType']=3
            obj['channelType']='c4441_all'
            channelList.append(obj)
#         channelList.reverse()
        return  channelList
    def videoParse(self, channel, url,channelType):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first('div',{"class":"mod channel-list"})
        if div!=None:
            divs = div.findAll("dl")
            if len(divs)==0:
                return False
            for item in divs:
                try:
                    ahref = item.first('a')
                    if ahref != None and  item.first("h3")!=None:
                        obj = {}
                        mp4Url = self.parseDomVideo(ahref.get("href"))
                        if mp4Url == None:
                            print '没有mp4 文件:', ahref.get("href")
                            continue
                        obj['url'] = mp4Url
                        img = ahref.first('img')
                        obj['pic'] = img.get('data-original')
                        obj['name'] = base64.b64decode(item.first("h3").text.replace("document.write(d('","").replace("'));",""))
                        print obj['name'],obj['url'],obj['pic']

                        videourl = urlparse(obj['url'])
                        obj['path'] = "c4441"+videourl.path
                        obj['updateTime'] = datetime.datetime.now()
                        obj['channel'] = channel
                        obj['baseurl'] = baseurl
                        dataList.append(obj)
                except Exception as e:
                    print common.format_exception(e)
                    pass
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj,"normal",baseurl,channelType)

        print 'c4441 video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        if len(dataList)==0:
            return False
        return True
    def parseDomVideo(self, url):
        try:
            content = self.fetchUrlContent(url)
            pattern = r'var playUrl=(\'|\")//(\'|\")\+[^+]+\+(\'|\")(/.*?\.m3u8)(\'|\")'
                # 执行匹配
            match = re.search(pattern, content)

            if match:
                play_url = match.group(4)  # 获取完整匹配
                return video_url+play_url.replace('var playUrl="//"+play+"', '').replace('/"','').replace('"','')
            else:
                print("未找到匹配的文本")
                print '没找到mp4'
                return None
        except Exception as e:
            print common.format_exception(e)
            return None


def videoParse(queue):
    queue.put(VideoParse())
