import httplib
from urlparse import urlparse

def get_status_code(url):
    """ This function retreives the status code of a website by requesting
        HEAD data from the host. This means that it only requests the headers.
        If the host cannot be reached or something else goes wrong, it returns
        None instead.
    """
    try:
        videourl = urlparse(url)
        conn = httplib.HTTPConnection(videourl.hostname,port=videourl.port,timeout=6000)
        conn.request("HEAD", videourl.path)
        return conn.getresponse().status
    except Exception as e :
        print e
        return None

if __name__ == '__main__':
    fh = open('../txt/video.txt')
    output = open('/var/video_out.txt', 'w')
    for line in fh.readlines():
        line.replace('\n', "").replace('\r', '')
        contents = line.split(",")
        status = get_status_code(contents[1]) 
       
        ret = "%s%s%s%s"%(contents[0],"->",status,"\n")
        print ret
        output.write(ret)   
