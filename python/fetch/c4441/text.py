#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import threading
from common.envmod import *
from common import common
from common import db_ops
from baseparse import *
from common import dateutil
from fetch.profile import *
import base64
global baseurl

class TextChannelParse(BaseParse):

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
        objs = self.textChannel()
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for channel in objs:
            ops.inertTextChannel(channel)
            print channel
        dbVPN.commit()
        dbVPN.close()
        for item in objs:
            print '开始解析频道---',item
            try:
                channel = item['url']
                for i in range(1, maxTextPage):
                    page_url = item['url']
                    if i==1:
                        page_url = '%s%s'%(page_url,"/index.html")
                    else:
                        page_url = '%s%s%s%s'%(page_url,'/index_',i,'.html')
                    print page_url
                    dbVPN = db.DbVPN()
                    ops = db_ops.DbOps(dbVPN)
                    count = self.update(page_url, ops, channel,item['name'])
                    dbVPN.commit()
                    dbVPN.close()
                    if count == 0:
                        break
            except Exception as e:
                print common.format_exception(e)
    def textChannel(self):
        objs = []
        ahrefs = self.header2()
        for ahref in ahrefs:
            obj = {}
            obj['name']=base64.b64decode(ahref.text.replace("document.write(d('","").replace("'));",""))
            obj['url']=ahref.get('href')
            obj['baseurl']=baseurl
            obj['updateTime']=datetime.datetime.now()
            obj['pic']=''
            obj['rate']=1.2
            obj['channel']=obj['url']
            obj['showType']=3
            obj['channelType']='normal'
            objs.append(obj)
        return objs

    def update(self, url, ops, channel,name):
        objs = self.fetchTextData(url, channel,name)
        print "解析Txt小说 ok----channl=", channel, '  数量=', len(objs)
        for obj in objs:
            try:
                ret = ops.inertTextItems(obj)
                if ret == None:
                    print 'text 已经存在，解析完毕'
            except Exception as e:   
                print  common.format_exception(e)
        return len(objs)

    def fetchTextData(self, url, channel,name):
        objs = []
        try:
            soup = self.fetchUrl(url)
            div = soup.first('div',{"class":"mod channel-list"})
            datalist = div.findAll('dl')
            sortType = dateutil.y_m_d()
            for item in datalist:
                ahref = item.first("a")
                if ahref!=None:
                    itemUrl = ahref.get("href")
                    try:
                        obj = {}
                        obj['fileDate'] = '11111'
                        obj['name'] = base64.b64decode(item.first("h3").text.replace("document.write(d('","").replace("'));",""))
                        print obj['name'],itemUrl
                        obj['url'] = itemUrl
                        obj['baseurl'] = baseurl
                        obj['channel'] = channel
                        obj['updateTime'] = datetime.datetime.now()
#                         self.t_queue.put(TextItemContentParse(ahref.get('href')))
                        ret = self.fetchText(itemUrl)
                        if ret==None:
                            print '没有文章数据',itemUrl
                            continue
                        obj['sortType'] = sortType
                        obj['channelName'] = name
                        objs.append(obj)
                    except Exception as e:
                        print  common.format_exception(e)
            return objs
        except Exception as e:
            print common.format_exception(e)
            return objs
    def fetchText(self,url):
        soup = self.fetchUrl(url)
        data = soup.first("div", {"class": "main book"})
        if data == None:
            data = soup.first("div", {"class": "pic"})
        if data != None:
            try:
                obj = {}
                obj['fileUrl'] = url
                obj['file'] = str(data)
                dbVPN = db.DbVPN()
                ops = db_ops.DbOps(dbVPN)
                ops.inertTextItems_item(obj)
                dbVPN.commit()
                dbVPN.close()
                print '解析文件 ', url,'完成'
                return 1
            except Exception as e:
                print common.format_exception(e)
        return None
        
#             print self.t_url, ' 解析完成'
#             return str(data)
#         return None
