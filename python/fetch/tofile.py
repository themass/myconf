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
from common import httputil
import re
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
queue = MyQueue.MyQueue(20000)
filePATH = "/home/file/book/"


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


class ChannelFetch(threading.Thread):

    def __init__(self, item):
        threading.Thread.__init__(self)
        self.t_item = item

    def run(self):

        try:
            dbVPN = db.DbVPN()
            ops = db_ops.DbOps(dbVPN)

            for i in range(0, 100):
                ret = ops.getTextChannelItems(self.t_item["url"], i)
                print '开始写入 channel ：', self.t_item["url"],
                cloase = False
                for item in ret:
                    path = filePATH + str(item['id']) + ".txt"
                    if os.path.exists(path):
                        cloase = True
                        break
                    output = open(path, 'w')
                    output.write(item['file'])
                    output.close()
                    print '写完文件：' + path
                if cloase == True:
                    break
            print 'channel ：', self.t_item["url"], '同步完成 len=', len(ret)
            dbVPN.close()
        except Exception as e:
            print common.format_exception(e)


def getAllChannel():
    dbVPN = db.DbVPN()
    ops = db_ops.DbOps(dbVPN)
    channels = ops.getTextChannel()
    for item in channels:
        queue.put(ChannelFetch(item))
    print 'channel len：', len(channels)
    dbVPN.close()
if __name__ == '__main__':

    for i in range(0, 30):
        worker = HandleThread("work-%s" % (i), queue)
        worker.start()
    getAllChannel()
