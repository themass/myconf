#!/usr/bin/python
# -*- coding: utf-8 -*-
import redis
REDIS_IP = 'm11010.zeus.redis.ljnode.com'
REDIS_PORT = 11010


def getRedis():
    pool = redis.ConnectionPool(host=REDIS_IP, port=REDIS_PORT)
    backup_redis = redis.Redis(connection_pool=pool)
    return backup_redis
