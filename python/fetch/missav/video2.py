#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse
from common import common
from urllib import unquote
import time
from fetch.profile import *
import logging

class VideoUserParse(BaseParse):

    def __init__(self):
        pass

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        # 生成从1到1400的数字
        numbers = list(range(1, 1401))
        # 每10个数字一组
        grouped_numbers = [numbers[i:i+10] for i in range(0, len(numbers), 10)]
        for group in grouped_numbers:
            first_number = group[0]  # 每组的第一个数字
            last_number = group[-1]  # 每组的最后一个数字
            chs = self.videoChannel(first_number, last_number)
            # for item in chs:
            #     print item
            #     ops.inertVideoUser(item)
            # print 'missav user video -- channel ok;,len=',len(chs)
            # dbVPN.commit()
            # dbVPN.close()
            for item in chs:
                for i in range(1, maxVideoPage):
                    url= "%s%s%s"%(item['url'],"?page=",i)
                    print url
                    con = self.videoParse(item['channel'], url,item['userId'])
                    print '解析完成 ', item['channel'], ' ---', i, '页'
                    if con==False:
                        print '没有数据了啊-======页数',i,'---',item['name'],item['url']
                        break
    def videoChannel(self, fromNum, toNum):
        channelList = []

        ahrefs = self.header(name="header2.html")
        for ahref in ahrefs:
            for i in range(fromNum, toNum):
                url= '%s?page=%s'%(ahref.get("href"),i)
                print '开始下载',url
                soup = self.fetchUrlWithBase(url)
                ul = soup.first("ul",{"class":"mx-auto grid grid-cols-2 gap-4 gap-y-8 sm:grid-cols-4 md:gap-6 lg:gap-8 lg:gap-y-12 xl:grid-cols-6 text-center"})
                if ul !=None:
                    lis =  ul.findAll("li")
                    count = 0
                    for item in lis:
                        # if i==5:
                        #     if count <8 :
                        #         count = count+1
                        #         print '忽略',i ,count
                        #         continue
                        div = item.first("div",{"class":"space-y-4"})
                        obj={}
                        obj['name']=div.first("h4").text
                        obj['url']=div.first("a").get('href')
                        obj['baseUrl']=baseurl
                        obj['updateTime']=datetime.datetime.now()
                        if div.first("img")!=None:
                            obj['pic']= div.first("img").get("src")
                        else:
                            obj['pic']=''
                        obj['rate']=1.2
                        obj['channel']='missav女优一览'
                        obj['userId']="missav"+obj['name']
                        obj['showType']=3
                        obj['channelType']='normal'
                        channelList.append(obj)
                print '下载ok', url
        print len(channelList)
        return channelList
    def videoParse(self, channel, url,userId):
        dataList = []
        soup = self.fetchUrlWithBase(url)
        divs = soup.findAll("div",{"class":"relative aspect-w-16 aspect-h-9 rounded overflow-hidden shadow-lg"})
        if len(divs)==0:
            print(soup)
            return False
        for item in divs:
            #name,pic,url,userId,rate,updateTime,path
            ahref = item.first('a')
            if ahref!=None:
                obj = {}
                mp4Url = self.parseDomVideo(ahref.get("href"))
                if mp4Url == None:
                    print '没有mp4 文件:', ahref.get("href")
                    continue
                obj['url'] = mp4Url
                imgdiv = ahref.first('video')
                obj['pic'] = imgdiv.get("data-src")
                obj['name'] = imgdiv.get("alt")
    
                videourl = urlparse(obj['url'])
                obj['path'] = userId+videourl.path
                obj['rate'] = 1.2
                obj['updateTime'] = datetime.datetime.now()
                obj['userId'] = userId
                obj['baseUrl'] = baseurl
                obj['showType'] = 3
                obj['channel'] = channel
                if mp4Url.count("m3u8")==0 and mp4Url.count("mp4")==0:
                    obj['videoType'] = "webview"
                else:
                    obj['videoType'] = "normal"
                print 'm3u8文件下载ok',obj['videoType'],obj['name'],mp4Url,obj['pic']
                dataList.append(obj)
                time.sleep(1)
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        for obj in dataList:
            ops.inertVideoUserItem(obj)

        print 'missav video --解析完毕 ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        if len(dataList)==0:
            return False
        return True

    def parseDomVideo(self, url):
        try:
            data = self.fetchUrlWithBaseText(url)
            mp4 =  parse_obfuscated_js(data)
            return mp4
        except Exception as e:
            print common.format_exception(e)
            return None
# def parserText(text):
#     match = re.search(r"eval\(function\(p,a,c,k,e,d\)\{.*?\}\('(.*?)',(\d+),(\d+),'(.*?)'\.split\('\|'\),(\d+),\{\}\)\)", text)
#     if match:
#         p = match.group(1)
#         a = int(match.group(2))
#         c = int(match.group(3))
#         k = match.group(4).split('|')
#         e = int(match.group(5))
#         d = {}
#         decoded_code = js_to_python(p, a, c, k, e, d)
#         liststr = decoded_code.split(";")
#         for item in liststr:
#             match = regVideo.search(item)
#             if match!=None:
#                 videoUrl =match.group(1)
#                 return "%s%s%s"%("http",videoUrl,'m3u8')
#     return None
#

def base36encode(number):
    """将数字转换为36进制字符串（兼容Python 2.7）"""
    if not isinstance(number, int):
        raise TypeError('Number must be an integer')
    if number < 0:
        return '-' + base36encode(-number)
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    base36 = ''
    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36
    return base36 or '0'

def decode_js_obfuscation(p, a, c, k, e=None, d=None):
    """
    解码常见的JavaScript混淆代码
    支持格式：eval(function(p,a,c,k,e,d){...}(...))
    """
    if d is None:
        d = {}

    # 创建替换字典
    for idx in range(c):
        key = base36encode(idx)
        d[key] = k[idx] if idx < len(k) and k[idx] else key

    # 执行变量替换
    for idx in range(c):
        if idx < len(k) and k[idx]:
            pattern = r'\b%s\b' % base36encode(idx)
            p = re.sub(pattern, k[idx], p)

    return p

def extract_m3u8_url(text):
    """
    从文本中提取m3u8视频URL
    支持完整URL和部分URL的提取与修复
    """
    # 提取完整URL
    full_url_pattern = r'(https?://[^"\';\s<>\[\]]+\.(?:m3u8|mp4|avi|flv|mov|wmv))'
    full_urls = re.findall(full_url_pattern, text)

    if full_urls:
        return full_urls[0]

    # 提取部分URL并修复
    partial_url_pattern = r'(https?://[^"\';\s<>\[\]]+)'
    partial_urls = re.findall(partial_url_pattern, text)

    for url in partial_urls:
        if '.m3u8' in url:
            clean_url = url.split('?')[0].split('#')[0]
            if not clean_url.endswith('.m3u8'):
                last_dot = clean_url.rfind('.')
                if last_dot != -1:
                    clean_url = clean_url[:last_dot] + '.m3u8'
                else:
                    clean_url += '.m3u8'
            return clean_url

    return None

def parse_obfuscated_js(html_content):
    """
    解析包含JavaScript混淆代码的HTML内容，提取视频URL
    """
    try:
        # 匹配混淆函数模式
        eval_pattern = r"eval\(function\(p,a,c,k,e,d\)\{.*?\}\('(.*?)',(\d+),(\d+),'(.*?)'\.split\('\|'\),(\d+),\{\}\)\)"
        match = re.search(eval_pattern, html_content)

        if not match:
            logging.info("未找到混淆的eval函数")
            return None

        # 提取混淆参数
        p = match.group(1)
        a = int(match.group(2))
        c = int(match.group(3))
        k = match.group(4).split('|') if match.group(4) else []
        e = int(match.group(5))

        # 解码混淆代码
        decoded_code = decode_js_obfuscation(p, a, c, k)

        # 提取视频URL
        return extract_m3u8_url(decoded_code)

    except Exception as e:
        logging.error("解析过程发生错误: %s", str(e))
        return None