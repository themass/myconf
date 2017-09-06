#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
import text_content
total_page = 100
page_size = 10


class TextItemsParse(threading.Thread):

    def __init__(self, obj, queue, page):
        self.t_obj = obj
        self.t_page = page
        self.t_queue = queue

    def run(self):
        param = {}
        param['action'] = 'list'
        param['pagesize'] = page_size
        param['pageindex'] = self.t_page
        param['type'] = self.t_obj.get('dir')
        data = httputil.postRequestWithParam(
            baseurl_text + textItemUrl, param, header)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        ret = data.get('data', [])
        sortType = dateutil.y_m_d()
        for item in ret:
            obj = {}
            obj['fileDate'] = ''
            obj['name'] = item.get('title', '')
            obj['url'] = textFileUrl + '/' + \
                sortType + "/" + str(item.get('id', 0))
            obj['baseurl'] = baseurl_text
            obj['channel'] = self.t_obj.get('url')
            obj['updateTime'] = datetime.datetime.now()
#             obj['file'] = self.parseText(item.get('id', 0))
            obj['sortType'] = sortType
            insRet = ops.inertTextItems(obj)
            if insRet == None:
                print 'text结束解析', obj
                break
            self.t_queue .put(
                text_content.TextItemsItem(obj, str(item.get('id', 0))))
        print 'dehyc channel=', self.t_obj['url'], '--解析完毕---', self.t_page, 'size=', len(ret)
        dbVPN.commit()
        dbVPN.close()


def textParse(queue):
    param = {}
    param['action'] = 'list'
    param['pid'] = 0
    data = httputil.postRequestWithParam(
        baseurl_text + textchannelUrl, param, header)
    ret = data.get('data', [])
    objs = []
    if len(ret) > 0:
        for item in ret:
            obj = {}
            obj['name'] = item.get('title', '性福之事') + "2"
            obj['baseurl'] = baseurl_text
            obj['url'] = textchannelUrl + '/' + str(item.get('id', 0))
            obj['dir'] = item.get('id', 0)
            obj['updateTime'] = datetime.datetime.now()
            for i in range(1, total_page):
                queue.put(TextItemsParse(obj, queue, i))
            objs.append(obj)
            print 'dehyc text channel=', obj['url'], '--加入队列'
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in objs:
            insRet = ops.inertTextChannel(obj)
        print 'dehyc text 更新channel ok ', len(objs)
        dbVPN.commit()
        dbVPN.close()
