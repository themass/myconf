#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import re
from common.envmod import *
from common import common
from common import db_ops
from baseparse import *
from common import dateutil
from fetch.profile import *

global baseurl

# 论坛分页可达 1000，不受全局 maxTextPage=60 限制
maxForumPage = 2000


class TextChannelParse(BaseParse):

    def __init__(self):
        pass

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
            print '开始解析频道---', item
            try:
                channel = item['url']
                first_url = self.pageUrl(item['url'], 1)
                first_soup = self.fetchUrl(first_url)
                max_page = self.getMaxPage(first_soup, item['url'])
                print '频道最大页=', max_page, item['name'], item['url']
                empty_pages = 0
                for i in range(1, max_page + 1):
                    page_url = self.pageUrl(item['url'], i)
                    print page_url, '(%s/%s)' % (i, max_page)
                    dbVPN = db.DbVPN()
                    ops = db_ops.DbOps(dbVPN)
                    list_count, ok_count = self.update(
                        page_url, ops, channel, item['name'],
                        soup=first_soup if i == 1 else None)
                    dbVPN.commit()
                    dbVPN.close()
                    if list_count == 0:
                        empty_pages += 1
                        print '本页无文章, empty=', empty_pages
                        if empty_pages >= 2:
                            print '连续空页，结束频道', item['name']
                            break
                    else:
                        empty_pages = 0
            except Exception as e:
                print common.format_exception(e)

    def pageUrl(self, channel_url, page):
        # /forum/19  -> /forum/19 或 /forum/19/2
        base = channel_url.rstrip('/')
        if page <= 1:
            return base
        return '%s/%s' % (base, page)

    def getMaxPage(self, soup, channel_url):
        """从分页链接解析最大页，如 /forum/19/1000"""
        max_page = 1
        prefix = channel_url.rstrip('/')
        try:
            for a in soup.findAll('a'):
                href = a.get('href') or ''
                # /forum/19/2 或 /forum/19?page=2
                m = re.match(r'^%s/(\d+)/?$' % re.escape(prefix), href)
                if m:
                    max_page = max(max_page, int(m.group(1)))
                    continue
                m = re.search(r'%s(?:/|\?).*?page=(\d+)' % re.escape(prefix), href)
                if m:
                    max_page = max(max_page, int(m.group(1)))
            for li in soup.findAll(['li', 'a'], {'class': re.compile('page')}):
                t = (li.text or '').strip()
                if t.isdigit() and 1 <= int(t) <= maxForumPage:
                    max_page = max(max_page, int(t))
        except Exception as e:
            print common.format_exception(e)
        if max_page > maxForumPage:
            max_page = maxForumPage
        if max_page < 1:
            max_page = maxTextPage
        return max_page

    def textChannel(self):
        objs = []
        ahrefs = self.header2()
        for ahref in ahrefs:
            obj = {}
            obj['name'] = ahref.text.strip()
            obj['url'] = ahref.get('href')
            obj['baseurl'] = baseurl
            obj['updateTime'] = datetime.datetime.now()
            obj['pic'] = ''
            obj['rate'] = 1.2
            obj['channel'] = obj['url']
            obj['showType'] = 3
            obj['channelType'] = 'normal'
            objs.append(obj)
        return objs

    def update(self, url, ops, channel, name, soup=None):
        list_count, objs = self.fetchTextData(url, channel, name, soup=soup)
        print "解析Txt小说 ok----channl=", channel, '  列表=', list_count, ' 入库=', len(objs)
        for obj in objs:
            try:
                ret = ops.inertTextItems(obj)
                if ret == None:
                    print 'text 已经存在，解析完毕'
            except Exception as e:
                print common.format_exception(e)
        return list_count, len(objs)

    def fetchTextData(self, url, channel, name, soup=None):
        try:
            if soup is None:
                soup = self.fetchUrl(url)
            datalist = soup.findAll("div", {"class": "colNovelList"})
            objs = []
            list_count = 0
            sortType = dateutil.y_m_d()
            for aitem in datalist:
                ahref = aitem.first("a")
                if ahref is None:
                    continue
                itemUrl = ahref.get("href")
                title_div = ahref.first("div", {"class": "container-title"})
                if title_div is None:
                    continue
                list_count += 1
                try:
                    obj = {}
                    obj['fileDate'] = '1111'
                    obj['name'] = title_div.text.strip()
                    print obj['name'], itemUrl
                    obj['url'] = itemUrl
                    obj['baseurl'] = baseurl
                    obj['channel'] = channel
                    obj['updateTime'] = datetime.datetime.now()
                    ret = self.fetchText(itemUrl)
                    if ret is None:
                        print '没有文章数据', itemUrl
                        continue
                    obj['sortType'] = sortType
                    obj['channelName'] = name
                    objs.append(obj)
                except Exception as e:
                    print common.format_exception(e)
            return list_count, objs
        except Exception as e:
            print common.format_exception(e)
            return 0, []

    def fetchText(self, url):
        soup = self.fetchUrl(url)
        data = soup.first("div", {"id": "photoShowPage"})
        if data is None:
            data = soup.first("div", {"class": re.compile(r'novelContent')})
        if data is not None:
            try:
                obj = {}
                obj['fileUrl'] = url
                obj['file'] = str(data)
                dbVPN = db.DbVPN()
                ops = db_ops.DbOps(dbVPN)
                ops.inertTextItems_item(obj)
                dbVPN.commit()
                dbVPN.close()
                print '解析文件 ', url, '完成'
                return 1
            except Exception as e:
                print common.format_exception(e)
        return None
