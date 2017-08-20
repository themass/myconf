#!/usr/bin/python
# -*- coding: utf-8 -*-
import redis
REDIS_IP = '10.33.106.34'
REDIS_PORT = 6379
def getRedis():
    print 'connect to backup info redis'
    pool = redis.ConnectionPool(host=REDIS_IP, port=REDIS_PORT)
    backup_redis = redis.Redis(connection_pool=pool)
    return backup_redis