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
    name = '第95期<!--[if lt IE 9 ]><![endif]-->2017/9/9<!--[if lt IE 9 ]><![endif]-->'
    strName = name.replace(
        "<!--[if lt IE 9 ]>", "").replace("<![endif]-->", "")
    name = html_parse.filter_tags(strName)
    print name