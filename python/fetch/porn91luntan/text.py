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

# Discuz 单版块可远超全局 maxTextPage(60)，本地上限按页码抓全
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
                # 先拉第1页，识别最大页码
                first_soup = self.fetchUrl("%s&page=1" % item['url'])
                max_page = self.getMaxPage(first_soup)
                print '频道最大页=', max_page, item['name'], item['url']
                empty_pages = 0
                for i in range(1, max_page + 1):
                    page_url = "%s&page=%s" % (item['url'], i)
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
                        print '本页无主题, empty=', empty_pages
                        if empty_pages >= 2:
                            print '连续空页，结束频道', item['name']
                            break
                    else:
                        empty_pages = 0
            except Exception as e:
                print common.format_exception(e)

    def getMaxPage(self, soup):
        """只从 div.pages 的 forumdisplay page= 解析。
        Discuz last 链接文字可能是 1663，但 href 常封顶 page=1000，以 href 为准。
        """
        max_page = 1
        try:
            for div in soup.findAll('div', {'class': 'pages'}):
                for a in div.findAll('a'):
                    href = a.get('href') or ''
                    if 'forumdisplay.php' not in href:
                        continue
                    m = re.search(r'page=(\d+)', href)
                    if m:
                        max_page = max(max_page, int(m.group(1)))
                for strong in div.findAll('strong'):
                    t = (strong.text or '').strip()
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
        ahrefs = self.header()
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

    def isStickyThread(self, subject):
        """置顶公告：tbody#stickthread_* 或 class 含 lock"""
        cls = (subject.get('class') or '').lower()
        if 'lock' in cls:
            return True
        parent = subject.parent
        # th -> tr -> tbody
        for _ in range(3):
            if parent is None:
                break
            pid = parent.get('id') or ''
            if pid.startswith('stickthread_'):
                return True
            parent = parent.parent
        return False

    def fetchTextData(self, url, channel, name, soup=None):
        try:
            if soup is None:
                soup = self.fetchUrl(url)
            # subject new / subject common 都要；排除置顶 stickthread / lock
            datalist = soup.findAll("th", {"class": re.compile(r'^subject')})
            objs = []
            list_count = 0
            sortType = dateutil.y_m_d()
            for subject in datalist:
                title_link = subject.find(
                    'a', href=re.compile(r'^viewthread\.php\?tid='))
                if title_link is None:
                    continue
                if self.isStickyThread(subject):
                    print '跳过置顶:', title_link.text.strip()
                    continue
                list_count += 1
                itemUrl = title_link.get('href')
                title = title_link.text.strip()
                try:
                    obj = {}
                    obj['fileDate'] = '1111'
                    obj['name'] = title
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
        if url is None:
            return None
        soup = self.fetchUrl(url)
        data = soup.findAll("div", {"class": "t_msgfontfix"})
        if data:
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
