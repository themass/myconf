import httplib
from urlparse import urlparse
import sys
reload(sys)
sys.setdefaultencoding('utf8')
def get_status_code(url,baseurl):
    """ This function retreives the status code of a website by requesting
        HEAD data from the host. This means that it only requests the headers.
        If the host cannot be reached or something else goes wrong, it returns
        None instead.
    """
    try:
        videourl = urlparse(url)
        conn = httplib.HTTPConnection(videourl.hostname,port=videourl.port,timeout=2000)
        headers={
                    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13', "Referer": baseurl}
        conn.request("HEAD", videourl.path,headers=headers)
        return conn.getresponse().status
    except Exception as e :
        print e
        return None

if __name__ == '__main__':
    if len(sys.argv)!=3:
        print 'args error ; inpt file, out putfile'
        return
    fh = open("%s%s"%('../txt/',sys.argv[1]))
    output = open("%s%s"%('/home/web/var/',sys.argv[2]), 'w')
    for line in fh.readlines():
        linestr = line.replace('\n', "").replace('\r', '')
        contents = linestr.split(",")
        if contents[2]=='http://yezmw.com':
            status = get_status_code(contents[1],contents[2]) 
            ret = "%s%s%s%s%s%s%s%s"%(contents[0],"->",status,"->",contents[2],"->",contents[1],"\n")
            print ret
            output.write(ret)   
    output.close()
    fh.close()
