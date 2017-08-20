#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime,threading
mutex = threading.RLock()
def now():
    return datetime.datetime.now()
def microsecond():
    return datetime.datetime.now().microsecond  

def yyyymmdd():
    return formatdate(None, '%Y%m%d')


def ymdHM():
    return formatdate(None, '%Y%m%d%H%M')


def y_m_d():
    return formatdate(None, '%Y-%m-%d')


def pre_ymd():
    return formatdate(datetime.datetime.now() - datetime.timedelta(days=1), '%Y%m%d')

def yesterday(format=None):
    if format==None:
        format = '%Y-%m-%d %H:%M:%S'
    return formatdate(datetime.datetime.now() - datetime.timedelta(days=1), format)

def beforeDay(day=0,format=None):
    if format==None:
        format = '%Y-%m-%d %H:%M:%S'
    return formatdate(datetime.datetime.now() - datetime.timedelta(days=day), format)

def hhMMss():
    return formatdate(None, '%H%M%S')


def hh_MM_ss():
    return formatdate(None, '%H-%M-%S')


def yyyymmddhhMMss():
    return formatdate(None, '%Y%m%d%H%M%S')

def y_m_dh_M_s():
    return formatdate(None, '%Y-%m-%d %H:%M:%S')


def y_m_dz_z_z():
    return formatdate(None, '%Y-%m-%d 00:00:00')


def formatdate(date=None,format=None):
    if date == None:
        date = datetime.datetime.now()
    if format == None:
        format = '%Y-%m-%d %H:%M:%S'
    with mutex:
        return datetime.datetime.strftime(date, format)


def formattodate(datestr,format=None):
    if None == format:
        format = '%Y-%m-%d %H:%M:%S'
    with mutex:
        return datetime.datetime.strptime(datestr, format)