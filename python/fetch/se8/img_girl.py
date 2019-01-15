#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import threading
from common import common
from baseparse import *
from common import db_ops
from common.envmod import *
from common import dateutil
from common import html_parse
from fetch.profile import *
global baseurl
nameStr = r"<.*>"

max_page = 10


class ImgGrilParse(BaseParse):

    def __init__(self, obj, queue):
        threading.Thread.__init__(self)
        self.t_obj = obj
        self.t_obj['rate'] = 1.1
        self.t_obj['showType'] = 3
        self.t_obj['channel'] = 'porn_sex'
        self.t_obj['channelType'] = 'porn_sex'
        self.t_queue = queue

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        url = self.t_obj['url']
        objs = self.fetchImgGrilChannel(url)
        for obj in objs:
            # and obj['url'].find('tubaobao.htm') == -1
            if obj['url'].find('/') != -1:
                ops.inertImgChannelWithChannel(obj,obj['channel'].replace("/?m=",''))
                self.t_queue.put(ParsImgChannel(obj))
                print '更新channel 完成，chennel数据事件加入队列,', obj['url']
            else:
                print '错误的url', obj
        dbVPN.commit()
        dbVPN.close()
    # 每一项都当成一个channel

    def fetchImgGrilChannel(self, url):
        soup = self.fetchUrl(url)
        objs = []
        table = soup.find('div',{"class":"box movie_list"})
        if table == None:
            print '没有 channel:', url
            return None
        aList = table.findAll('a')
        for item in aList:
            obj = {}
            obj['url'] = item.get('href')
            obj['baseurl'] = baseurl
            img = item.find('img')
            if img != None:
                obj['pic'] = img.get('data-original')
            else:
                obj['pic'] = None
            obj['updateTime'] = dateutil.y_m_d()
            obj['rate'] = 1.4
            obj['showType'] = 3
            obj['channel'] = 'porn_sex'
            obj['channelType'] = 'porn_sex'
            obj['name'] = self.fetchImgGrilChannelName(item.get('href'))
            print obj
            objs.append(obj)
        return objs

    def fetchImgGrilChannelName(self, url):
        soup = self.fetchUrl(url)
        p = soup.find("span", {"class": 'cat_pos_l'})
        if p != None:
            return p.text.replace("您的位置：", "").replace("首页", "").replace(" ", "").replace("&nbsp;", '').replace("»","").replace("极品美女","")
        return "girl"


class ParsImgChannel(BaseParse):

    def __init__(self, obj):
        threading.Thread.__init__(self)
        self.t_obj = obj

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for i in range(1, maxImgPage):
            objs = self.fetchGirlChannelData(i)
            print "解析 Girl channel图片ok----channel=", self.t_obj['url'], ' size=', len(objs)
            for obj in objs:
                try:
                    sortType = dateutil.y_m_d()
                    obj['sortType'] = sortType
                    ops.inertImgItems(obj)
                    print 'items ：', obj['url'],obj['channel'], " piclen=", len(obj['picList'])
                    for picItem in obj['picList']:
                        item = {}
                        item['itemUrl'] = obj['url']
                        item['picUrl'] = picItem
                        item['origUrl'] = picItem
                        ops.inertImgItems_item(item)
    #                     print 'items_item ：', obj
                    dbVPN.commit()
                except Exception as e:
                    print common.format_exception(e)
        dbVPN.commit()
        dbVPN.close()

    def fetchGirlChannelData(self,i):
        objs = []
        page = self.t_obj['url'].replace(".html","-") + str(i) + ".html"
        items = self.fetchgirlChannelItems(page)
        print '解析完成',page
        objs.extend(items)
        return objs

    def fetchgirlChannelItems(self, url):
        try:
            soup = self.fetchUrl(url)
            div = soup.find("div", {"class": 'box movie_list'})
            objs = []
            if div != None:
                alist = div.findAll("a")
                for item in alist:
                    if item.get("href")!=None and item.get("href").count("tubaobaolist") > 0:
                        objs.extend(self.fetchTubaobaoList(item.get("href")))
                        continue
                    obj = self.fetchgirlChannelItemsOne(item)
                    objs.append(obj)
            return objs
        except Exception as e:
            print common.format_exception(e)
    def fetchTubaobaoList(self, url):
        soup = self.fetchUrl(url)
        div = soup.find("div", {"class": 'box movie_list'})
        objs = []
        if div != None:
            ul = div.find('ul')
            if ul != None:
                alist = ul.findAll("a")
                for item in alist:
                    if item.get("href").count("javascript")>0:
                        continue
                    obj = self.fetchgirlChannelItemsOne(item)
                    objs.append(obj)
        print url,'tubobolist',len(objs)
        return objs

    def fetchgirlChannelItemsOne(self, item):
        obj = {}
        obj['url'] = item.get("href")
        strName = item.text.replace(
            "[if lt IE 9 ]>", "").replace("<![endif]", "")
        obj['name'] = html_parse.filter_tags(strName)
        span = item.first('span')
        if span != None:
            obj['fileDate'] = html_parse.filter_tags(span.text.replace(
                "[if lt IE 9 ]>", "").replace("<![endif]", ""))
            obj['name'] = obj['name'].replace(obj['fileDate'], '')
        else:
            obj['fileDate'] = ''
        obj['channel'] = self.t_obj['url'].replace("/?m=",'')
        obj['updateTime'] = dateutil.y_m_d()
        obj['baseurl'] = baseurl
        pics = self.fetchImgs(item.get("href"))
        obj['pics'] = len(pics)
        obj['picList'] = pics
        obj['showType'] = 3
        print obj['url'],'解析完毕',obj['channel'],len(pics),obj['name']
        return obj

    def fetchImgs(self, url):
        soup = self.fetchUrl(url)
        picData = soup.first("div", {"class": "content"})
        if picData == None:
            return []
        picList = picData.findAll("img")
        pics = []
        for item in picList:
            pics.append(item.get('data-original'))
        return pics
