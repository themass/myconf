#!/usr/bin/python
# -*- coding: utf-8 -*-

from functools import partial
from operator import is_not


def propertyFetch(data, key):
    res = []
    for item in data:
        res.append(item[key])
    return res


def listToMap(data, key):
    res = {}
    for item in data:
        res[item[key]] = item
    return res


def listToMuiltMap(data, key):
    res = {}
    for item in data:
        var = res.get(item[key], None)
        if var == None:
            var = []
        var.append(item)
        res[item[key]] = var
    return res


def listRemove(data, val):
    return filter(partial(is_not, val), data)


def listReplace(data, val, replace):
    for i in range(len(data)):
        if data[i] == val:
            data[i] = replace


def printData(obj):
    if obj == None:
        print 'is None'
    elif isinstance(obj, list):
        for item in obj:
            print item
    elif isinstance(obj, dict):
        for key, val in obj.items():
            print key, val
    else:
        print obj
