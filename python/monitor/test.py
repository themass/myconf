import httplib
from urlparse import urlparse
import sys
reload(sys)
sys.setdefaultencoding('gbk')
def paresFile(name):
    data = ''
    with open(name, 'r') as f:
        data = f.read()
    obj = data.split("\n")
    dataMap = {}
    for items in obj:
        item = items.split(",")
        v = dataMap.get(item[1],[])
        v.append(item[0])
        dataMap[item[1]]=v
    print len(dataMap)
    for k,v in dataMap.items():
        print "#",k  
        for host in v:
            print "client %s{\nsecret        = FreeVPN@vpn5296\nshortname    = vpn_check\n}"%(host)
        print "#",k," end"
        
if __name__ == '__main__':
    paresFile('../txt/1003.txt')
    