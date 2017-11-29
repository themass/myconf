#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
import threading
from common.envmod import *
from common import common
from common import typeutil
from common import db_ops
from common import MyQueue
from common import httputil
from common import dateutil
import re
import sys
from urlparse import urlparse

reload(sys)
sys.setdefaultencoding('utf8')
baseurl = "http://116.62.181.149:8080"
header = {'User-Agent': 'okhttp/2.5.0'}
freeurl = '/json2/free.php'
vipurl = '/json2/vipLevel.php'
personurl = '/json2/confidential.php'

maxPage = 500


def parseFreePage(url):
    param = {}
    param['level'] = '1'
    param['pay_Id'] = 'cgsswitfpass'
    param['package'] = 'com.ffn.qudkuh'
    param['imei'] = '354112070307165'
    param['v'] = '9.15'
    param['appid'] = '7'
    param['play'] = 'play'
    param['page'] = 1
    objs = httputil.getData(baseurl + url, param, header)
    return objs.get('totalPage', 0) + 1


def parseFree(page, url, channel):
    param = {}
    param['level'] = '1'
    param['pay_Id'] = 'cgsswitfpass'
    param['package'] = 'com.ffn.qudkuh'
    param['imei'] = '354112070307165'
    param['v'] = '9.15'
    param['appid'] = '7'
    param['play'] = 'play'
    dataList = []
    param['page'] = page
    objs = {}
    try:
        objs = httputil.getData(baseurl + url, param, header)
    except Exception as e:
        return dataList
    objsCom = objs.get('con', [])
    for item in objsCom:
        obj = {}
        obj['name'] = item.get('title', "")
        obj['url'] = item.get('video', "")
        if obj['url'] == '':
            continue
        obj['pic'] = item.get('pic', "")
        obj['channel'] = channel
        obj['rate'] = '1.2'
        videourl = urlparse(obj['url'])
        obj['path'] = videourl.path
        obj['updateTime'] = datetime.datetime.now()
        dataList.append(obj)
    return dataList


def parseUserOnePage(userid=None):
    param = {}
    param['pay_Id'] = 'cgsswitfpass'
    param['package'] = 'com.ffn.qudkuh'
    param['channel'] = '100'
    param['imei'] = '354112070307165'
    param['v'] = '9.15'
    param['appid'] = '7'
    param['sjc'] = '1511892560401'
    param['key'] = 'e35c1bee07b9d38763cdf84a3abe65fe'
    if userid != None:
        param['userId'] = userid
    param['page'] = 1
    objs = httputil.getData(baseurl + personurl, param, header)
    return objs.get('totalPage', 0) + 1


def parseUserOne(page, userid=None):
    param = {}
    param['pay_Id'] = 'cgsswitfpass'
    param['package'] = 'com.ffn.qudkuh'
    param['channel'] = '100'
    param['imei'] = '354112070307165'
    param['v'] = '9.15'
    param['appid'] = '7'
    param['sjc'] = '1511892560401'
    param['key'] = 'e35c1bee07b9d38763cdf84a3abe65fe'
    if userid != None:
        param['userId'] = userid
    param['page'] = page
    dataList = []
    try:
        objs = httputil.getData(baseurl + personurl, param, header)
    except Exception as e:
        return dataList
    objsCom = objs.get('con', [])
    for item in objsCom:
        obj = {}
        obj['name'] = item.get('shareTItle', "")
        obj['nickName'] = item.get('nickName', "")
        obj['url'] = item.get('videoPlayAddress', "")
        if obj['url'] == '':
            continue
        videourl = urlparse(obj['url'])
        obj['path'] = videourl.path
        obj['pic'] = item.get('imgAddress', "")
        obj['channel'] = 'qvod_user'
        obj['rate'] = '1.2'
        obj['userId'] = item.get('userId', "")
        obj['updateTime'] = datetime.datetime.now()
        obj['headPic'] = item.get('headImg', "")
        dataList.append(obj)
    return dataList
