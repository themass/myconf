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
reload(sys)
sys.setdefaultencoding('utf8')
# http://www.dehyc.com
baseurl = "http://www.dehyc.com"
baseurl_text = 'http://58.84.54.38:8010'
soundUrl = '/api/dirlist.ashx'
soundItemUrl = '/api/mp3data.ashx'
textchannelUrl = '/api/category.ashx'
textItemUrl = '/api/bookdata.ashx'
textFileUrl = '/api/bookdata.ashx'
header = {'User-Agent': 'okhttp/3.3.1'}
