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
if __name__ == '__main__':
    nameStr = '<.*>'
    re_comment = re.compile('<!--.*-->')
    name = '<!--[if lt IE 9 ]><span class="bg_top"><![endif]-->2017/9/9<!--[if lt IE 9 ]></span><span class="bg_tail"></span><![endif]-->'
    name = name.replace("<!--[if lt IE 9 ]>", "").replace("<![endif]-->", "")
    result, number = re.subn(nameStr, '', name)
    print html_parse.filter_tags(name)
