#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
from common.envmod import *
import novel941_vip
import se8_vip
import sp878_vip
import g6858_vip
import kedouwo_vip
import ddd804_vip
import kpd36_vip
from fetch import  bx88222_vip
def pase1():
#     novel941_vip.parseText()
#     kedouwo_vip.parseText12()
#     g6858_vip.parseText()
#     ddd804_vip.parsetextddd804()
#     ddd804_vip.parsetext65aeae()
    
    kpd36_vip.parseText()
    bx88222_vip.parseText()
    sp878_vip.parseText()
def pase2():
    
    se8_vip.startWork()
    se8_vip.parseText()
    novel941_vip.parseText2()
    ####mayi01_vip.parseText()
if __name__ == '__main__':
    val = argsMap.get("-p",0)
    if int(val)==1:
        pase1()
    elif int(val)==2:
        pase2()
    
    