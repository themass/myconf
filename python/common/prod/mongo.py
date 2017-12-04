#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
通用库配置
"""
from common.base import mongo_db


host = '10.10.35.28:27021,10.10.35.29:27021,10.10.35.30:27021'
username = 'xte'
password = 'fn_xte_rw'
replicaSet = 'mongodb://%s:%s@%s/?replicaSet=fn' % (username, password, host)
print replicaSet


def order(**params):
    return mongo_db.mongo_collection(replicaSet, 'fn_xte', 'orderInfo', params)


def jobHistory(**params):
    return mongo_db.mongo_collection(replicaSet, 'fn_xte', 'jobHistory', params)
