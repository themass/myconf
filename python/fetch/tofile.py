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
from common import dateutil
from common import html_parse
import re
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
queue = MyQueue.MyQueue(20000)
filePATH = "/home/file/book/"
filePATHWeb = "/home/file/book_web/"
filePATHHtml = "/home/file/book_html/"
class ChannelFetch(threading.Thread):

    def __init__(self, item):
        threading.Thread.__init__(self)
        self.t_item = item

    def run(self):

        try:
            dbVPN = db.DbVPN()
            ops = db_ops.DbOps(dbVPN)
#             sortType = dateutil.y_m_d()
            sortType = "2019-03-24"
            for i in range(0, 20000):
                #                 ret = ops.getTextChannelItems(self.t_item["url"], i)
                ret = ops.getTextChannelItemsById(i, sortType)
                if len(ret) == 0:
                    print '写入完毕'
                    break
                print '开始写入 channel ：', self.t_item["url"],
                cloase = False
                for item in ret:
#                     path = filePATH + str(item['id']) + ".txt"
#                     if os.path.exists(path) == False:
#                         output = open(path, 'w')
#                         output.write(item['file'])
#                         output.close()
#                         print '写完文件：' + path
#                     path = filePATHWeb + str(item['id']) + ".txt"
#                     if os.path.exists(path) == False:
#                         output = open(path, 'w')
#                         output.write(html_parse.filter_tags(item['file']))
#                         output.close()
#                         print '写完文件：' + path
                    path = filePATHHtml + str(item['id']) + ".html"
#                     if os.path.exists(path) == False:
                    output = open(path, 'w')
                    output.write(
                        html_parse.txtToHtml(html_parse.filter_tags(item['file'])))
                    output.close()
                    print '写完文件：' + path
                print '写完页', i
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
        break
    print 'channel len：', len(channels)
    dbVPN.close()
if __name__ == '__main__':

    #     getAllChannel()
    item = {}
    item['url'] = "test"
    fetch = ChannelFetch(item)
    fetch.run()
