#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
环境变量解析
"""
import sys
import getopt


def usage():
    print "-e", "  :  ", "val= prod or test  ,prodmod or testmod"
    print "-m", "  :  ", "val=count , run once and consume val"
    print "-c", "  :  ", "val=count ,multithread thread count"
    print "-h", "  :  ", "help"
    sys.exit()
options, args = getopt.getopt(sys.argv[1:], "e:m:c:h")
prodEnv = False
mod = False
onceCount = 0
multi = False
multiCount = 0
for name, val in options:
    print name, val
    if name in ("-e"):
        if val == 'prod':
            prodEnv = True
        else:
            prodEnv = False
    elif name in ("-m"):
        mod = True
        onceCount = int(val)
    elif name in ("-c"):
        multi = True
        multiCount = int(val)
    elif name in ("-h"):
        usage()
if prodEnv:
    from prod import *
else:
    from test import *
