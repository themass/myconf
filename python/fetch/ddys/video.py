#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse, parse_qs
from common import common
from fetch.profile import *
import sys
import time
import re
reload(sys)
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
        print 'ddys video -- channel ok;,len=', len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            genre = self.genreFromUrl(item['url'])
            channelType = item['channelType']
            for i in range(1, maxVideoPage):
                con = self.videoParse(item['channel'], genre, i, channelType)
                if con == False:
                    print '没有数据了 - 页数', i, '---', item['name'], item['url']
                    break
                print '解析完成 ', item['channel'], ' ---', i, '页'

    def genreFromUrl(self, url):
        # movie?genre=action
        qs = urlparse('?' + url.split('?', 1)[-1]).query if '?' in url else ''
        if not qs and 'genre=' in url:
            qs = url.split('?', 1)[-1]
        params = parse_qs(qs)
        vals = params.get('genre') or []
        return vals[0] if vals else ''

    def videoChannel(self):
        channelList = []
        ahrefs = self.header()
        for ahref in ahrefs:
            obj = {}
            obj['name'] = ahref.text.strip()
            obj['url'] = ahref.get('href')
            obj['baseurl'] = baseurl
            obj['updateTime'] = datetime.datetime.now()
            obj['pic'] = ''
            obj['rate'] = 1.2
            obj['channel'] = 'ddys' + obj['name']
            obj['showType'] = 3
            obj['channelType'] = 'movie'
            channelList.append(obj)
        return channelList

    def videoParse(self, channel, genre, page, channelType):
        dataList = []
        try:
            list_url = '%s/movies?type=movie&genre=%s&page=%s&per_page=%s' % (
                apiBase, genre, page, perPage)
            payload = self.fetchJson(list_url)
            if not payload or not payload.get('success'):
                return False
            items = payload.get('data') or []
            if len(items) == 0:
                return False
            for item in items:
                slug = item.get('slug')
                if not slug:
                    continue
                mp4Url = self.parseDomVideo(slug)
                if mp4Url is None:
                    print '没有m3u8 文件:', slug
                    continue
                obj = {}
                obj['url'] = mp4Url
                obj['pic'] = item.get('poster') or ''
                obj['name'] = item.get('title') or slug
                path = item.get('url') or ('/movie/%s' % slug)
                if not path.startswith('http'):
                    path = baseurl.rstrip('/') + path
                obj['path'] = path
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                obj['baseurl'] = baseurl
                print channel, obj['name'], obj['url'], obj['pic']
                dataList.append(obj)

            dbVPN = db.DbVPN()
            ops = db_ops.DbOps(dbVPN)
            for obj in dataList:
                ops.inertVideo(obj, "normal", baseurl, channelType)
            print 'ddys video --解析完毕 ; channel =', channel, '; len=', len(dataList), list_url
            dbVPN.commit()
            dbVPN.close()
            time.sleep(0.3)
        except Exception as e:
            print common.format_exception(e)
        if len(dataList) == 0:
            return False
        return True

    def pickM3u8(self, url):
        """sources 里偶发多集拼接: HD国语$url1#HD中字$url2，取第一个 m3u8"""
        if not url:
            return None
        if 'm3u8' not in url:
            return None
        # 多源用 # 分隔
        for part in url.split('#'):
            part = part.strip()
            if '$' in part:
                part = part.split('$', 1)[-1]
            if 'm3u8' in part and part.startswith('http'):
                return part
        found = re.search(r'https?://[^\s\'"#]+?\.m3u8[^\s\'"#]*', url)
        return found.group(0) if found else None

    def parseDomVideo(self, slug):
        try:
            src_url = '%s/movies/%s/sources' % (apiBase, slug)
            payload = self.fetchJson(src_url)
            if not payload or not payload.get('success'):
                return None
            data = payload.get('data') or {}
            online = data.get('online') or []
            for src in online:
                murl = self.pickM3u8(src.get('url'))
                if murl:
                    return murl
            print '没找到m3u8', slug
            return None
        except Exception as e:
            print common.format_exception(e)
            return None


def videoParse(queue):
    queue.put(VideoParse())
