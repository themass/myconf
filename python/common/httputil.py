#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import json
import urllib
import ssl
import common
import StringIO
import gzip
import requests
DEFULT_ENCODEING = 'utf-8'
DEFULT_TIMEOUT = 20


def postRequestWithBody(url, data={}, header={}):
    try:
        datastr = json.dumps(data)
        req = urllib2.Request(url, headers=header)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        resp = opener.open(req, datastr, timeout=DEFULT_TIMEOUT).read()
        return json.loads(resp, encoding=DEFULT_ENCODEING)
    except Exception as e:
        raise HTTPException('url=%s' % (url), ex=e)


def postRequestWithParam(url, data={}, header={}):
    try:
        datastr = urllib.urlencode(data)
        req = urllib2.Request(url, headers=header)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        resp = opener.open(req, datastr, timeout=DEFULT_TIMEOUT).read()
        return json.loads(resp, encoding=DEFULT_ENCODEING)
    except Exception as e:
        raise HTTPException('url=%s' % (url), ex=e)


def getData(url, data={}, header={}):
    try:
        datastr = urllib.urlencode(data)
        url = "%s?%s" % (url, datastr)
        req = urllib2.Request(url, headers=header)
        apidata = urllib2.urlopen(req, timeout=DEFULT_TIMEOUT).read()
        return json.loads(apidata, encoding=DEFULT_ENCODEING)
    except Exception as e:
        print common.format_exception(e)
        raise HTTPException('url=%s' % (url), ex=e)


def getText(url, data={}, header={}, isGzip=False):
    try:
        datastr = urllib.urlencode(data)
        url = "%s?%s" % (url, datastr)
        req = urllib2.Request(url, headers=header)
        req.add_header('Accept-encoding', 'gzip')
        res = urllib2.urlopen(req, timeout=DEFULT_TIMEOUT)
#         isGzip = res.headers.get('Content-Encoding')
        if isGzip:
            compresseddata = res.read()
            compressedstream = StringIO.StringIO(compresseddata)
            gzipper = gzip.GzipFile(fileobj=compressedstream)
            return gzipper.read()
        else:
            return res.read().decode('utf8', errors="ignore")
    except Exception as e:
        print common.format_exception(e)
        raise HTTPException('url=%s' % (url), ex=e)


def getTextByRequst(url, data={}, header={}):
    datastr = urllib.urlencode(data)
    url = "%s?%s" % (url, datastr)
    resp = requests.get(url, headers=header)
    return resp.text


class HTTPException(Exception):

    def __init__(self, msg, ex=None):
        self.exMsg = common.format_exception(ex)
        Exception.__init__(self, msg)

    def getEx(self):
        return self.exMsg
