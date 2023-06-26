#!/usr/bin python
# -*- coding: utf-8 -*-
from common.envmod import *
from fetch import novel941_vip
from fetch import noval1024_vip


def pase1():
    novel941_vip.parseText()
    noval1024_vip.parseText()
    noval1024_vip.parseText2()


if __name__ == '__main__':
    pase1()
    
    