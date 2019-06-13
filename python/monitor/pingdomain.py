# -*- coding: utf-8 -*-
from common import db_ops
from common import httputil
import os
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
reg = re.compile(
    r"rtt min/avg/max/mdev = ([0-9\.]+)/([0-9\.]+)/([0-9\.]+)")

domainList=['104.233.198.193',
'144496.com',
'185.232.15.107',
'192.240.120.34',
'201605mp4.11bubu.com',
'201606mp4.11bubu.com',
'2016mp4.11bubu.com',
'201712mp4.89soso.com',
'2017mp4.11bubu.com',
'2017mp4.54popo.com',
'201806.53didi.com',
'23.225.126.178',
'2mp4.11bubu.com',
'4mp4.11bubu.com',
'5.9.40.198',
'5mp4.11bubu.com',
'67.229.33.139',
'6mp4.11bubu.com',
'7mp4.11bubu.com',
'8mp4.11bubu.com',
'91.196.222.18',
'avjdvideo.com',
'axhd.xyz',
'baidu.com-y-qq.com',
'bi.xunleiab.com',
'bi.xunleief.com',
'bi.xunleigh.com',
'bo.cdn-dns-youku.com',
'bo.cnd-163.com',
'bo.cnd-letv.com',
'bo.cnd-tuduo.com',
'bo.cnd-youku.com',
'bo.ixx-baidu.com',
'cdn.800zy99.com',
'cdn.801zy.com',
'cdn.812zy.com',
'cdn.846u.com',
'cdn.cn2-163.com',
'cdn.cn2-baidu.com',
'cdn.cn2-tuduo.com',
'cdn.cn2-youku.com',
'cdn.zyw605.org',
'cdn1-youku.akbvip.com',
'cdn1.91baimi.com',
'cdn1.much365.com',
'cdn1.polaroidchina.com',
'cdn1.thsinfo.com',
'cdn1.zyw605.org',
'cdn2-youku.jshuajiu.com',
'cdn2.diexuewang.com',
'cdn2.polaroidchina.com',
'cdn2.senhaige.com',
'cdn2.zyw605.org',
'cdn3-baidu.dsd666.com',
'cdn3.senhaige.com',
'cdn5.beiyun100.com',
'cdn790.91youku-iqiyi.com',
'cdnb.cdn-youku-cn.com',
'cdnf.fsmalaban.com',
'cdnh.xzmuzhipin.com',
'cdnk.kaifengaudio.com',
'cdnvideo99.52homedecor.com',
'cdnvideos.52homedecor.com',
'ck.c8c3.com',
'ck.ckbfq.com',
'cn2.163-cn2.com',
'cn2.baidu-cn2.com',
'cn2.letv-cn2.com',
'cn2.tuduo-cn2.com',
'cn2.youku-cn2.com',
'cnhttps',
'dadi-bo.com',
'dadi-yun.com',
'email.v88dizhi.at.gmail.baidudu.space',
'ginocdn.bybzj.com',
'gs.xxx-ooo.xyz',
'hd1.o0omvo0o.com',
'hls2-l3.xvideos-cdn.com',
'hp.cdnbyte.top',
'ifeng.com-sohu.com',
'ifeng.com-y-baidu.com',
'imagetupian.nypd520.com',
'img.801zy.com',
'index.m3u8',
'kkembed.kdwembed.com',
'lajiao-bo.com',
'lr.991video.com',
'm3u8.299du.com',
'm3u8.40cdn.com',
'm3u8.46cdn.com',
'm3u8.91panzy.com',
'm3u8.cdnpan.com',
'm3u8.lililitv.com',
'm3u801.moviessl001.com',
'mp4.luplayer.com',
'mp4.zzvip.tv',
'ok.yun-cdnkan.com',
'p.672sp.com',
'play.168168bo.com',
'play.169169bo.com',
'play.bfdzym.com',
'play.bo159159.com',
'play.cdmbo.com',
'play.dapaobo.com',
'py.xhsyun.xyz',
'qiyucdn.com',
'qq.cdn-dns-youku.com',
'qq.com-h-ifeng.com',
'qq.com-y-ifeng.com',
'sezhanwang.net',
'sp.8app.net',
'v-pptv.com',
'v-tudou.com',
'v.8xzizizi1.com',
'v.tscdn88.com',
'v2.14mp4.com',
'video.6606686.com',
'video.baidu-taobao.top',
'video.caomin5168.com',
'video.dnsoy.com',
'video.feimanzb.com',
'video.gujianzhixiang.com',
'video.jiagew762.com',
'video.lllwo2o.com',
'video.luersuo.com',
'video.qqdaiguaxitong.com',
'video.yjf138.com',
'video.ypshe2.info',
'video1.ddbtss.com',
'video1.dnsoy.com',
'video1.feimanzb.com',
'video1.rhsj520.com',
'video1.tripsmc.com',
'video1.yancheng85.com',
'video2.bamintese.com',
'video2.caomin5168.com',
'video2.ddbtss.com',
'video2.dnsoy.com',
'video2.fxsdp.com',
'video2.gujianzhixiang.com',
'video2.jiagew762.com',
'video2.tripsmc.com',
'video3.tripsmc.com',
'videocdn.dlyilian.com',
'videocdn.hndtl.com',
'videocdn.quweikm.com',
'videocdn2.quweikm.com',
'videocdnbaidu.rhsj520.com',
'videos.yuncdnkan.com',
'videox3.ju1zhe.com',
'vo.ppptoppp.com',
'vod.6606686.com',
'vod.6718999.com',
'www.6225588.com',
'www.avjdvideo.com',
'www.avjidiwang.com',
'www.fkc123.net',
'www.tupianyuming.com',
'www.vod.nkanav1.com',
'www.vod.nkanav2.com',
'yaseav.cn',
'youku.cdn-baidu-com.com',
'youku.com-bilibili.com',
'youku.com-iqiyi.com',
'youku.com-y-youku.com',
'yun.iixx-yun.com',
'zy0.xstuff.cn',]


def myAlign(string, length=0):
    if length == 0:
        return string
    slen = len(string)
    re = string
    if isinstance(string, str):
        placeholder = ' '
    else:
        placeholder = u'　'
    while slen < length:
        re += placeholder
        slen += 1
    return re


def parse(pingtexts):
    for line in pingtexts:
        if line.count("rtt min") > 0:
            match = reg.search(line)
            return match.group(2)
    return 10000

if __name__ == '__main__':
    errorList = []
    for item in domainList:
        cmd = 'ping  -c 2 -w 2 %s' % (item)
        lines = os.popen(cmd).readlines()
        num = parse(lines)
        if num == 10000:
            errorList.append(item)
    print errorList
    sys.exit()
