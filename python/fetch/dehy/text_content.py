#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from common import common


class TextItemsItem(threading.Thread):

    def __init__(self, obj, textId):
        self.t_id = textId
        self.t_obj = obj

    def run(self):
        try:
            param = {}
            param['action'] = 'bookfile'
            param['id'] = self.t_id
            data = httputil.getTextByRequst(
                baseurl_text + textFileUrl, param, header)
            dbVPN = db.DbVPN()
            ops = db_ops.DbOps(dbVPN)
            obj = {}
            obj['fileUrl'] = self.t_obj.get('url')
            obj['file'] = data
            ops.inertTextItems_item(obj)
            print 'dehyc file=', self.t_obj['url'], '--解析完毕---'
            dbVPN.commit()
            dbVPN.close()
        except Exception as e:
            print common.format_exception(e)
