#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
import threading
from BeautifulSoup import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def fetchUrl(url):
    req = urllib2.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Linux; U; Android 8.0.0; zh-cn; HWI-AL00 Build/HUAWEIHWI-AL00) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30', "Referer":url
                ,"Host": "yepu.swapdox.com","Accept-Encoding": "gzip",
                "T-Token": "sPl1gaqimReMELUvMQ4s8w==","X-ONEX-AUTH":"" })
#     req.encoding = 'utf-8'
    response = urllib2.urlopen(req, timeout=3000)
    gzipped = response.headers.get(
        'Content-Encoding')  # 查看是否服务器是否支持gzip
    content = response.read().decode('utf8', errors='replace').replace("<![endif]-->","")
    return  BeautifulSoup(content)
if __name__ == '__main__':
    ips = ["175.152.49.50",
            "221.182.7.82",
           "223.75.64.226",
           "183.95.239.2",
           "111.8.194.148",
           "210.22.52.50",
           "120.195.194.147",
           "221.182.7.90",
           "58.49.96.219",
           "61.160.97.50",
           "112.81.148.82",
           "61.183.233.226",
           "220.249.89.50",
           "119.4.61.170",
           "221.182.8.82",
           "112.103.170.241",
           "218.76.92.231",
           "111.40.55.181",
           "175.152.49.58",
           "171.217.121.2",
           "144.123.27.66",
           "223.78.116.227",
           "221.0.78.36",
           "61.181.179.110",
           "111.42.50.2",
           "221.238.149.226",
           "59.49.203.204",
           "111.28.249.122",
           "153.0.157.193",
           "39.164.45.209",
           "111.9.5.97",
           "111.172.10.251",
           "112.21.11.75",
           "36.148.242.109",
           "111.183.82.5",
           "182.148.200.134",
           "120.202.182.113",
           "39.144.148.75",
           "27.18.29.246",
           "114.224.0.214",
           "10.16.41.174",
           "203.168.1.27",
           "58.44.250.151",
           "112.3.7.144",
           "183.210.224.6",
           "113.57.66.248",
           "117.152.73.29",
           "182.240.55.191",
           "58.44.251.237",
           "183.210.224.38",
           "125.68.100.82",
           "59.174.146.25",
           "125.69.9.25",
           "171.216.139.178",
           "111.183.22.107",
           "59.174.144.180",
           "223.70.242.2",
           "113.57.66.227",
           "59.174.83.76",
           "117.152.159.88",
           "125.71.94.248",
           "110.188.95.92",
           "171.213.48.95",
           "36.148.241.70",
           "114.253.39.44",
           "111.172.11.220",
           "153.35.27.58",
           "36.148.240.73",
           "116.169.2.248",
           "36.170.59.103",
           "110.53.234.252",
           "117.151.24.64",
           "180.130.10.196",
           "111.197.234.152",
           "218.76.82.228",
           "223.104.238.204",
           "110.188.95.158",
           "220.197.194.36",
           "111.172.9.177",
           "117.84.42.250",
           "220.197.235.238",
           "171.113.62.87",
           "171.83.53.34",
           "117.136.66.68",
           "117.61.113.156",
           "220.113.127.27",
           "125.33.200.202",
           "49.76.145.72",
           "223.64.204.38",
           "124.232.26.252",
           "111.172.11.59",
           "111.181.141.152",
           "111.201.29.119",
           "58.19.73.126",
           "171.221.148.10",
           "112.22.111.42",
           "221.227.42.99",
           "121.60.81.84",
           "117.152.214.180",
           "117.154.106.180",
           "116.169.2.16",
           "112.22.79.108",
           "211.161.175.132",
           "110.53.234.186",
           "117.152.75.55",
           "117.61.109.154",
           "183.95.251.204",
           "39.164.45.210",
           "120.226.196.237",
           "120.244.202.94",
           "114.225.26.122"]
    jiips = ["111.28.249.122",
             "111.40.55.181-184",
             "111.42.50.2-4",
             "111.8.194.148",
             "112.103.170.241-245",
             "112.81.148.82",
             "119.4.61.170-174",
             "120.195.194.147",
             "144.123.27.66",
             "153.0.157.193",
             "171.217.121.2-4",
             "175.152.49.50-54",
             "175.152.49.58-62",
             "183.95.239.2",
             "210.22.52.50",
             "218.76.92.231",
             "220.249.89.50",
             "221.0.78.36",
             "221.182.7.82-89",
             "221.182.7.90-94",
             "221.182.8.82-89",
             "221.238.149.226",
             "223.75.64.226",
             "223.78.116.227",
             "58.49.96.219",
             "59.49.203.204",
             "61.160.97.50",
             "61.181.179.110",
             "61.183.233.226"]
    yip = []
    for ip in jiips:
           if ip.count("-")>0:
                  ipds = ip.split(".")
                  ipdsf = ipds[3].split("-")
                  for i in range(int(ipdsf[0]),int(ipdsf[1])+1):
                      str = "%s.%s.%s.%s"%(ipds[0],ipds[1],ipds[2],i)
                      yip.append(str)
           else:
                  yip.append(ip)
    print yip
    for i in ips:
        if yip.count(i)==0:
            print i


    # baseurl = "https://www.asy1000.com/"
    # header = {'User-Agent':
    #       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36', "Referer": baseurl,
    #       "cookie":"Hm_lvt_64f3b8e72697945612104f755f0e6ce4=1557163354; __51cke__=; Hm_lpvt_64f3b8e72697945612104f755f0e6ce4=1557164611; __tins__19425543=%7B%22sid%22%3A%201557163355132%2C%20%22vd%22%3A%2010%2C%20%22expires%22%3A%201557166411669%7D; __51laig__=10",
    #       "X-Requested-With":"XMLHttpRequest"}
    # str = '{"isdv":1,"type":5,"ispass":1,"url":"https://tv2.youkutv.cc/2020/08/29/BKdKI8YSVGmW5QPN/playlist.m3u8'
    # content = str.replace('"', "").split("url:")
    # shareVideo = re.compile(r"http(.*?)/2020/(.*?)")
    # for text in content:
    #     print(text)
    #     match = shareVideo.search(text)
    #     if match!=None:
    #         print(match.group(0), "-------", match.group(1), "-------", match.group(2))
#     videoId = re.compile("(.*\/)(\d+)\.html")
#     match = videoId.search('dongzuopian/202006/91671.html')
#     if match!=None:
#         
#         Id= match.group(2)
#         print match.group(1),Id
#         url  = 'vod-play-id-%s-src-1-num-1.html'%(Id)
#         print url
#     soup= fetchUrl("http://yepu.swapdox.com/api/ShortVideo/AddWahtchRecord/cak?newsId=c6d3d478-e65c-44cf-931f-5863074b7788")
#     print soup
    #print soup.findAll("div",{"class":"x3 margin-top"})
#     fcntl.flock('', fcntl.LOCK_EX)
#     data = {}
#     data['id']="1844"
#     ret = httputil.postRequestWithParam("http://www.fuli750.com/api/payvideo.html", data, header)
#     print ret
#     dbVPN = db.DbVPN()
#     ops = db_ops.DbOps(dbVPN)
#     obj = {}
#     obj['url'] = 'https://520cc.club/embed/136726.mp4'
#     obj['pic'] = ''
#     obj['name'] = 'test520ccwebview'
#     obj['path'] = 'test520ccwebview'
#     obj['updateTime'] = datetime.datetime.now()
#     obj['channel'] = 'test'
#     obj['videoType'] = "fanqiang"
#     obj['baseurl'] = 'https://520cc.club'
#     ops.inertVideo(obj,'webview','https://520cc.club','fanqiang')
#     
#     obj['url'] = 'https://1fgm8js.oloadcdn.net/dl/l/bwM0AoKhnaKk1_II/F9ESsEd1Qw0/5b7056b1da6d3.mp4?mime=true'
#     obj['pic'] = ''
#     obj['name'] = 'test520ccnormal'
#     obj['path'] = 'test520ccnormal'
#     obj['updateTime'] = datetime.datetime.now()
#     obj['channel'] = 'test'
#     obj['videoType'] = "fanqiang"
#     obj['baseurl'] = 'https://520cc.club'
#     ops.inertVideo(obj,'normal','https://520cc.club','fanqiang')
# 
#     dbVPN.commit()
#     dbVPN.close()
#     regVideo = re.compile(r'getmovurl\.html", {id:(.*?),td:(.*?)},')
#     str = '$.post("/index/getmovurl.html", {id:15699,td:2},'
#     match = regVideo.search(str)
#     print match.group(1),match.group(2)
#     iframeVideo = re.compile(r"onclick=\"window.open\('magnet(.*?)','_self'\)")
#     str = "str: \"<tr onmouseover=\"this.style.backgroundColor='#F4F9FD';this.style.cursor='pointer';\" onmouseout=\"this.style.backgroundColor='#FFFFFF'\" height=\"35px\" style=\"border-top: 1px solid rgb(221, 221, 221); background-color: rgb(255, 255, 255); cursor: pointer;\">\r\n    <td width=\"70%\" onclick=\"window.open('magnet:?xt=urn:btih:C05D741E9F2CC7E991E06FAB854136584763B78E&dn=DIC-017_CAVI','_self')\">\r\n        <a style=\"color:#333\" rel=\"nofollow\" title=\"滑鼠右鍵點擊並選擇【複製連結網址】\" href=\"magnet:?xt=urn:btih:C05D741E9F2CC7E991E06FAB854136584763B78E&dn=DIC-017_CAVI\">DIC-017_CAVI  字幕<\/a>\r\n            <\/td>\r\n    <td style=\"text-align:center;white-space:nowrap\" onclick=\"window.open('magnet:?xt=urn:btih:C05D741E9F2CC7E991E06FAB854136584763B78E&dn=DIC-017_CAVI','_self')\">\r\n        <a style=\"color:#333\" rel=\"nofollow\" title=\"滑鼠右鍵點擊並選擇【複製連結網址】 href=\"magnet:?xt=urn:btih:C05D741E9F2CC7E991E06FAB854136584763..."
#     match = iframeVideo.search(str)
#     print match,match.group(1)
#     regVideo = re.compile(r"encrypt\((.*), 'E', \$key\);")
#     str = "$play=encrypt(https://youku.cdn-tudou.com/20180508/5819_7b1f8025/index.m38, 'E', $key);"
#     match = regVideo.search(str)
#     print matc
#     print os.popen("wget http://api.ourder.com:8080/video/ssl/player.aspx?c=0515055a4c1e494f494e&w=640&h=400").read()
#     driver = webdriver.Chrome()
#     driver.get("http://api.ourder.com:8080/video/ssl/player.aspx?c=0515055a4c1e494f494e&w=640&h=400")
#     print driver.page_source
#     print requests.get("http://api.ourder.com:8080/video/ssl/player.aspx?c=0515055a4c1e494f494e&w=640&h=400").text
#     str = '''
#     var vHLSurl    = "//"+avod+"/19/2018/07/LjVbWE7U/LjVbWE7U.m3u8";
#     '''
#     playVideo = re.compile(r'varvHLSurl="//"\+avod\+"(.*?)m3u8')
#     match = playVideo.search(str.replace(" ", ""))
#     print "%s%s%s"%("https://cdn.846u.com",match.group(1),"m3u8")