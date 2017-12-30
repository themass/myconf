#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
import json
sys.setdefaultencoding('utf8')


class VideoParse(threading.Thread):

    def __init__(self, queue):
        self.queue = queue

    def run(self):
        self.freeParse('qvod_free', freeurl, 2)
        pages = parseFreePage(vipurl)
        print 'vip  ', pages
        self.freeParse('qvod_vip', vipurl, pages)
#         pages = parseUserOnePage()
#         print 'user  ', pages
#         self.personParse(pages)

    def freeParse(self, channel, url, pages):
        for page in range(1, pages):
            data = parseFree(page, url, channel)
            if len(data) == 0:
                break
            dbVPN = db.DbVPN()
            ops = db_ops.DbOps(dbVPN)
            for obj in data:
                ops.inertVideo(obj)
            print 'qvod vip audio --解析完毕 ;len=', len(data), ' ;page=', page
            dbVPN.commit()
            dbVPN.close()

    def personParse(self, pages):
        userList = []
        for page in range(1, pages):
            data = parseUserOne(page, None)
            if len(data) == 0:
                break
            dbVPN = db.DbVPN()
            ops = db_ops.DbOps(dbVPN)
            for obj in data:
                ops.inertVideoUser(obj)
            print 'user 解析完毕；page=', page, 'len=', len(data)
            dbVPN.commit()
            dbVPN.close()
            for obj in data:
                if obj.get('userId', None) == None:
                    continue
                if userList.count(obj.get('userId')) == 0:
                    userList.append(obj.get('userId'))
                else:
                    continue
                self.queue.put(VideoUserItemParse(obj.get('userId')))


class VideoUserItemParse(threading.Thread):

    def __init__(self, userId):
        self.userId = userId

    def run(self):

        pages = parseUserOnePage(self.userId)
        for page in range(1, pages):
            data = parseUserOne(page, self.userId)
            if len(data) == 0:
                break
            dbVPN = db.DbVPN()
            ops = db_ops.DbOps(dbVPN)
            for obj in data:
                ops.inertVideoUserItem(obj)
            print 'user item解析完毕；page=', page, 'userId=', self.userId, 'len=', len(data)
            dbVPN.commit()
            dbVPN.close()


def videoParse(queue):
    queue.put(VideoParse(queue))
