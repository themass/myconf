#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
import threading
from BeautifulSoup import BeautifulSoup
from common.envmod import *
from common import common
from common import typeutil
from common import db_ops
from common import MyQueue
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
baseurl = "https://www.bbb965.com"
reg = re.compile(r"(.*\/)\d+\.htm")
mp3Name = re.compile(r"<span>.*</span>")
queue = MyQueue.MyQueue(200)
maxCount = 5


def fetchUrl(url):
    count = 0
    while count < maxCount:
        try:
            req = urllib2.Request(baseurl + url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13', "Referer": "https://www.bbb670.com/htm/index.htm"})
            content = urllib2.urlopen(req, timeout=300).read()
            soup = BeautifulSoup(content)
            return soup
        except Exception as e:
            print '打开页面错误,重试', baseurl + url, '次数', count

    print '打开页面错误,重试3次还是错误', baseurl + url
    return BeautifulSoup('')


def fetchHead(name):
    try:
        url = "/htm/index.htm"
        soup = fetchUrl(url)
        menus = soup.findAll("ul", {"class": "menu mt5"})
        for menu in menus:
            active = menu.first("li", "active").text
            if active.count(name) > 0:
                return menu.findAll("li")
    except Exception as e:
        print common.format_exception(e)


def parsHeadText(lis):
    data = {}
    objs = []
    for li in lis:
        a = li.first("a")
        if a.get("href") != "/":
            data[a.get("href")] = a.text
    for url, name in data.items():
        obj = {}
        obj['name'] = name
        obj['baseurl'] = baseurl
        obj['url'] = url
        obj['updateTime'] = datetime.datetime.now()
        objs.append(obj)
    return objs


def parsFirstPage(url):
    soup = fetchUrl(url)
    divs = soup.findAll("div", {"class": "pagination"})
    if len(divs) > 0:
        aAll = divs[len(divs) - 1].findAll("a")
        for a in aAll:
            if a.text.count(u"上一页") > 0:
                href = a.get('href')
                match = reg.search(href)
                if match == None:
                    return None
                return match.group(1)
    else:
        divs = soup.findAll("div", {"class": "pageList"})
        if len(divs) > 0:
            aAll = divs[len(divs) - 1].findAll("a")
            for a in aAll:
                if a.text.count(u"上一页") > 0:
                    href = a.get('href')
                    match = reg.search(href)
                    if match == None:
                        return None
                    return match.group(1)
    return None


class FileParse(threading.Thread):

    def __init__(self, obj, channel):
        threading.Thread.__init__(self)
        self.t_obj = obj
        self.t_channel = channel

    def run(self):
        print '解析列表页 channel：', self.t_channel
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        try:
            url = self.t_obj['url']
            first = parsFirstPage(url)
            print '分页', first
            if first != None:
                for i in range(1, 100):
                    url = first + str(i) + ".htm"
                    count = self.update(url, ops)
                    dbVPN.commit()
                    if count == 0:
                        break
            else:
                self.update(url, ops)
                dbVPN.commit()
            dbVPN.close()
        except Exception as e:
            print common.format_exception(e)
            dbVPN.commit()
            dbVPN.close()

    def update(self, url, ops):
        objs = self.fetchFileData(url, self.t_channel)
        print threading.current_thread().getName(), "解析有声小说  mp3 ok----数据items=", len(objs), '--channel:', self.t_channel
        for obj in objs:
            ops.inertSoundFile(obj)
        return len(objs)

    def fetchMp3(self, url):
        soup = fetchUrl(url)
        audio = soup.find("audio")
        if audio != None:
            return audio.get('src')

        return None

    def fetchFileData(self, url, channel):
        try:
            soup = fetchUrl(url)
            datalist = soup.findAll("ul", {"class": "textList"})
            objs = []
            for item in datalist:
                ahrefs = item.findAll("a")
                for ahref in ahrefs:
                    obj = {}
                    span = ahref.first('span')
                    if span != None:
                        obj['fileDate'] = span.text
                    else:
                        obj['fileDate'] = ''
                    name = ahref.text.replace(obj['fileDate'], '')
                    obj['name'] = name
                    obj['url'] = ahref.get('href')
                    obj['baseurl'] = baseurl
                    obj['channel'] = channel
                    obj['updateTime'] = datetime.datetime.now()
                    mp3 = self.fetchMp3(ahref.get('href'))
                    if mp3 == None:
                        print '没有mp3文件--', ahref, '---', url
                        continue
                    obj['file'] = mp3
                    objs.append(obj)
            return objs
        except Exception as e:
            print common.format_exception(e)


class ChannelParse(threading.Thread):

    def __init__(self, obj):
        threading.Thread.__init__(self)
        self.t_obj = obj

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        try:
            url = self.t_obj['url']
            first = parsFirstPage(url)
            print first
            if first != None:
                for i in range(1, 100):
                    url = first + str(i) + ".htm"
                    count = self.update(url, ops)
                    dbVPN.commit()
                    if count == 0:
                        break
            else:
                self.update(url, ops)
                dbVPN.commit()
            dbVPN.close()
        except Exception as e:
            print common.format_exception(e)
            dbVPN.commit()
            dbVPN.close()

    def update(self, url, ops):
        lis = self.fetchDataHead(url)
        objs = self.parsDataText(lis)
        print "解析有声小说 ok----channl数=", len(objs)
        for obj in objs:
            ops.inertSoundChannel(obj)
            queue.put(FileParse(obj, obj['url']))
        return len(objs)

    def fetchDataHead(self, url):
        try:
            soup = fetchUrl(url)
            lis = soup.findAll("li")
            return lis

        except Exception as e:
            print common.format_exception(e)

    def parsDataText(self, lis):
        objs = []
        for li in lis:
            a = li.first("a")
            obj = {}
            obj['name'] = a.text
            obj['baseurl'] = baseurl
            obj['url'] = a.get('href')
            obj['updateTime'] = datetime.datetime.now()
            obj['pic'] = a.find('img').get('src', "")
            objs.append(obj)
        return objs


class TextChannelParse(threading.Thread):

    def __init__(self, obj):
        threading.Thread.__init__(self)
        self.t_obj = obj

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        ops.inertTextChannel(self.t_obj)
        dbVPN.commit()
        print self.t_obj
        try:
            url = self.t_obj['url']
            channel = url
            first = parsFirstPage(url)
            print first, url
            if first != None:
                for i in range(1, 50):
                    url = first + str(i) + ".htm"
                    count = self.update(url, ops, channel)
                    dbVPN.commit()
                    if count == 0:
                        break
            else:
                self.update(url, ops, channel)
                dbVPN.commit()

            dbVPN.close()
        except Exception as e:
            print common.format_exception(e)
            dbVPN.commit()
            dbVPN.close()

    def update(self, url, ops, channel):
        objs = self.fetchTextData(url, channel)
        print "解析Txt小说 ok----channl=", channel, '  数量=', len(objs)
        for obj in objs:
            ops.inertTextFile(obj)
        return len(objs)

    def fetchTextData(self, url, channel):
        try:
            soup = fetchUrl(url)
            datalist = soup.findAll("ul", {"class": "textList"})
            objs = []
            for item in datalist:
                ahrefs = item.findAll("a")
                for ahref in ahrefs:
                    obj = {}
                    span = ahref.first('span')
                    if span != None:
                        obj['fileDate'] = span.text
                    else:
                        obj['fileDate'] = ''
                    name = ahref.text.replace(obj['fileDate'], '')
                    obj['name'] = name
                    obj['url'] = ahref.get('href')
                    obj['baseurl'] = baseurl
                    obj['channel'] = channel
                    obj['updateTime'] = datetime.datetime.now()
                    txt = self.fetchText(ahref.get('href'))
                    if txt == None:
                        print '没有Txt文件--', ahref, '---', url
                        continue
                    obj['file'] = txt
                    objs.append(obj)
            return objs
        except Exception as e:
            print common.format_exception(e)

    def fetchText(self, url):
        soup = fetchUrl(url)
        data = soup.first("div", {"class": "novelContent"})
        if data != None:
            print url, ' 解析完成'
            return str(data)
        return None


class HandleThread(threading.Thread):

    def __init__(self, name, queue):
        threading.Thread.__init__(self, name=name)
        self.t_name = name
        self.t_queue = queue

    def run(self):
        while(True):
            try:
                print queue.qsize()
                obj = queue.get(timeout=30)
                obj.run()
            except Exception as e:
                print threading.current_thread().getName(), '---conti'
                pass


def parseSound():
    lis = fetchHead(u"有声小说")
    objs = parsHeadText(lis)
    print "解析有声小说 ok----项目=", len(objs)
    for obj in objs:
        queue.put(ChannelParse(obj))


def parseText():
    lis = fetchHead(u"情色小说")
    objs = parsHeadText(lis)
    print "解析有情色小说 ok----项目=", len(objs)
    for obj in objs:
        queue.put(TextChannelParse(obj))
        print obj
if __name__ == '__main__':

    for i in range(0, 30):
        worker = HandleThread("work-%s" % (i), queue)
        worker.start()
#     parseSound()
    parseText()
