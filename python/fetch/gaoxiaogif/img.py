#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import threading
from common import common
from baseparse import *
from common import db_ops
from common.envmod import *
from common import dateutil
global baseurl
import sys
from urlparse import urlparse
reload(sys)
sys.setdefaultencoding('utf8')


class ImgParse(BaseParse):

    def __init__(self,):
        threading.Thread.__init__(self)
        self.t_obj = {}
        self.t_obj['name'] = "搞笑动态图"
        self.t_obj['baseurl'] = baseurl
        self.t_obj['url'] = '/index.html'
        self.t_obj['updateTime'] = datetime.datetime.now()
        self.t_obj['rate'] = 1.2
        self.t_obj['showType'] = 3
        self.t_obj['channel'] = 'gaoxiao_gif'

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        ops.inertImgChannel(self.t_obj)
        dbVPN.commit()
        # 有分页
        sortType = dateutil.y_m_d()
        for i in range(1, maxImgChannelPage):
            url = self.t_obj['url']
            if i!=1:
                url = self.t_obj['url'].replace('.html','')+'_'+str(i)+'.html'
            print url
            pics = self.fetchDataHead(url)   
            print '解析',i,'页','len=',len(pics)
            for item in pics:
                obj = {}
                obj['name'] = item['name']
                obj['channel'] = self.t_obj['url']
                obj['updateTime'] = datetime.datetime.now()
                obj['fileDate'] = ''
                obj['baseurl'] = baseurl
                obj['showType'] = 3
        #             obj['url'] = url.replace("&", "")
                obj['url'] = urlparse(item['url']).path
                print obj['url']
        #             obj['pics'] = len(pics)
                obj['pic'] = item['url']
                obj['sortType'] = sortType
                pics = []
                obj['pics'] = 1
                ops.inertImgItems(obj)
                picitem = {}
                picitem['itemUrl'] = obj['url']
                picitem['picUrl'] = item['url']
                ops.inertImgItems_item(picitem)
                dbVPN.commit()

    def fetchDataHead(self, url):
        try:
            soup = self.fetchUrl(url)
            alist = []
            ul = soup.first("ul", {'class': 'gif_pic'})
            if ul != None:
                lis = ul.findAll('li')
                for li in lis:
                    ahref = li.first('a')
                    if ahref!=None:
                        obj ={}
                        picUrl= self.fetchImgItemData(ahref.get('href'))
                        if picUrl!=None:
                            obj['url']=picUrl
                            obj['name'] = li.first('span',{'class':'text'}).text   
                            print obj['name'] 
                            alist.append(obj)
            return alist

        except Exception as e:
            print common.format_exception(e)

    def fetchImgItemData(self, url):
        try:
            soup = self.fetchUrl(url)
            div = soup.first("div",{'class':'listgif-giftu content_pic'})
            if div!=None:
                return div.first("img").get('src')
        except Exception as e:
            print common.format_exception(e)
            return None
