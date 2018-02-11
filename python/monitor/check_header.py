import httplib
from urlparse import urlparse

def get_status_code(url,baseurl):
    """ This function retreives the status code of a website by requesting
        HEAD data from the host. This means that it only requests the headers.
        If the host cannot be reached or something else goes wrong, it returns
        None instead.
    """
    try:
        videourl = urlparse(url)
        conn = httplib.HTTPConnection(videourl.hostname,port=videourl.port,timeout=6000)
        headers={
                    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13', "Referer": baseurl}
        conn.request("HEAD", videourl.path,headers=headers)
        return conn.getresponse().status
    except Exception as e :
        print e
        return None

if __name__ == '__main__':
    fh = open('../txt/video.txt')
    output = open('/home/web/var/video_out1.txt', 'w')
    for line in fh.readlines():
        linestr = line.replace('\n', "").replace('\r', '')
        contents = linestr.split(",")
        status = get_status_code(contents[1],contents[2]) 
       
        ret = "%s%s%s%s%s%s%s%s"%(contents[0],"->",status,"->",contents[2],"->",contents[1],"\n")
        print ret
        output.write(ret)   
    output.close()
    fh.close()
