#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
通用库配置
"""
from common.base import mongo_db

host = '10.33.106.237:27017'
username = 'xte'
password = '123456'
db = 'xte'
replicaSet = 'mongodb://%s:%s@%s/%s' % (username, password, host, db)


def order(**params):
    return mongo_db.mongo_collection(replicaSet, 'xte', 'orderInfo', params)


def jobHistory(**params):
    return mongo_db.mongo_collection(replicaSet, 'xte', 'jobHistory', params)
