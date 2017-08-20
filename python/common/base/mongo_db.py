#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Mongo连接配置
"""
from pymongo import ReadPreference, MongoClient

DEFAULT_READ_PREFERENCE = ReadPreference.SECONDARY_PREFERRED

#默认write concern取值
# -1:Errors Ignored
#  0:Unacknowledged
#>=1:N nodes Acknowledged (数据同步到N个节点后返回，包含主节点，如果N大于复本集内节点数据，会一直阻塞)
DEFAULT_WRITE_CONCERN = 1


def mongo_collection(host, db, table, params):
    """
    创建连接并返回mongo collection

    :Parameters:
    - 'host': mongo地址，以mongodb://开头
    - 'db' 数据库名
    - 'table' 表名
    - 'params' 可选参数，类型为map，可包含字段r,w，分别用于覆盖默认的read preference和write concern
    """
    client = MongoClient(host,
                         read_preference=params.get('r', DEFAULT_READ_PREFERENCE),
                         w=params.get('w', DEFAULT_WRITE_CONCERN),
                         connect=False)
    return client[db][table]


def mongo_client(host, params):
    return MongoClient(host,
                       read_preference=params.get('r', DEFAULT_READ_PREFERENCE),
                       w=params.get('w', DEFAULT_WRITE_CONCERN),
                       connect=False)