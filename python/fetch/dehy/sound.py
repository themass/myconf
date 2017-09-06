#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *

channel_size = 100
item_page_size = 10000
item_commit_size = 5


class SoundItemParse(threading.Thread):

    def __init__(self, obj):
        self.t_obj = obj

    def run(self):
        param = {}
        param['action'] = 'mp3list'
        param['pagesize'] = item_page_size
        param['pageindex'] = 1
        param['dirid'] = self.t_obj.get('dir')
        data = httputil.postRequestWithParam(
            baseurl + soundItemUrl, param, header)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        ret = data.get('data', [])
        sortType = dateutil.y_m_d()
        index = 0
        for item in ret:
            obj = {}
            obj['fileDate'] = ''
            obj['name'] = item.get('mp3_title', '')
            obj['url'] = soundItemUrl
            obj['baseurl'] = baseurl
            obj['channel'] = self.t_obj.get('url')
            obj['updateTime'] = datetime.datetime.now()
            obj['file'] = item.get('mp3_url', '')
            obj['sortType'] = sortType
            insRet = ops.inertSoundItems(obj)
            index = index + 1
            if (index % item_commit_size) == 0:
                dbVPN.commit()
            if insRet == None:
                print 'sound结束解析', obj
                break
        print 'dehyc channel=', self.t_obj['url'], '--解析完毕'
        dbVPN.commit()
        dbVPN.close()


def SoundParse(queue):
    param = {}
    param['action'] = 'dirlist'
    param['pagesize'] = channel_size
    param['pageindex'] = 1
    param['type'] = 0
    data = httputil.postRequestWithParam(baseurl + soundUrl, param, header)
    ret = data.get('data', [])
    objs = []
    if len(ret) > 0:
        for item in ret:
            obj = {}
            obj['name'] = item.get('dir_title', '性福之事')
            obj['baseurl'] = baseurl
            obj['url'] = soundUrl + '/' + str(item.get('dir_id', 0))
            obj['dir'] = item.get('dir_id', 0)
            obj['updateTime'] = datetime.datetime.now()
            obj['pic'] = item.get('dir_img_url', '')
            queue.put(SoundItemParse(obj))
            objs.append(obj)
            print 'dehyc channel=', obj['url'], '--加入队列'
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in objs:
            ops.inertSoundChannel(obj)
        print 'dehyc 更新channel ok ', len(objs)
        dbVPN.commit()
        dbVPN.close()
