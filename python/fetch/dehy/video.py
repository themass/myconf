#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
import json
sys.setdefaultencoding('utf8')
from urlparse import urlparse


class VideoParse(threading.Thread):

    def __init__(self):
        pass

    def run(self):
        for channel, url in videoUrl.items():
            try:
                self.videoParse(channel, url)
            except Exception as e:
                print e
                print common.format_exception(e)

    def videoParse(self, channel, url):
        dataStr = httputil.getText(url, {}, header)
        print dataStr.encode('utf-8')
        print type(dataStr)
        print type(dataStr.encode('utf-8'))
        data = json.loads(dataStr.encode('utf-8'), "utf-8")
        ret = data.get('data', [])
        dataList = []
        for item in ret:
            obj = {}
            obj['name'] = item.get('mp4_title', '')
            obj['url'] = item.get('mp4_url', '')
            if obj['url'] == '':
                continue
            videourl = urlparse(obj['url'])
            obj['path'] = videourl.path
            obj['updateTime'] = datetime.datetime.now()
            obj['pic'] = item.get('mp4_img', '')
            obj['channel'] = channel
            dataList.append(obj)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideo(obj)

        print 'dehyc audio --解析完毕 ; channel =', channel, '; len=', len(dataList)
        dbVPN.commit()
        dbVPN.close()


def videoParse(queue):
    queue.put(VideoParse())
