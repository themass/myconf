#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf8')
def paresFile2(name,count):
    data = ''
    dataMap = {}
    with open(name, 'r') as f:
        data = f.readlines()
    for item in data:
        if item.count('staging') !=0:
            continue
        obj = item.replace('\n','').split(",")
        if len(obj)!=count:
            print obj
            continue
        dataMap[obj[0]] = obj
    # obj = data.split(",")
    # dataMap[obj[0]] = obj
    # for item in obj:
    #     print item
        # if item.count(",")==8:
        #     items = item.split(",#")
        #     print items[1]
        #     dataMap.append(items[0])
    print '-----', dataMap
    return dataMap
if __name__ == '__main__':
    dataMap1 = paresFile2('t1',3)
    dataMap2 = paresFile2('t2',5)
    for key,val in dataMap1.items():
        obj = dataMap2.get(key,None)
        if obj!=None:
            val.append(obj[2])
            val.append(obj[3])
            val.append(obj[4])
            str1 = ','.join([str(x) for x in val])
        else:
            str1 = ','.join([str(x) for x in val])
            print str1