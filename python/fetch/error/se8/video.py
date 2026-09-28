#!/usr/bin python
# -*- coding: utf-8 -*-
from baseparse import *
from urlparse import urlparse, parse_qs
from common import common
from fetch.profile import *
import hashlib
import time
import re
import base64
import json
import subprocess

MAOMI_VIDEO_HOST = 'https://kwmdmmsp.hongtaitanghua.com'
MAOMI_SIGN_KEY = 'D7hGKHnWThaECaQ3ji4XyAF3MfYKJ53M'
MAOMI_API_HOST = 'https://iofbsmcxzs.692fo7w1.com'
MAOMI_URI_PREFIX = 'gt6ikshg458mns4f'
MAOMI_AES_KEY_B64 = 'SWRUSnEwSGtscHVJNm11OGlCJU9PQCF2ZF40SyZ1WFc='
MAOMI_AES_IV_B64 = 'JDB2QGtySDdWMg=='
reMaomiFullUrl = re.compile(
    r'https?://[^"\']*hongtaitanghua\.com[^"\']+\.m3u8\?[^"\']+')
reMaomiVideoPath = re.compile(
    r'(/common/impulses/[^"\']+\.m3u8)')
reMaomiPostId = re.compile(
    r'(?:post-detail|play)[/-](\d+)|/video/[^/]+/(\d+)(?:$|[/?#])')
reMaomiVideoUrlJson = re.compile(r'"video_url"\s*:\s*"([^"]+)"')
reMaomiListPath = re.compile(
    r'(?:page|video)/([^/]+)/([^/?#]+?)(?:\.html)?(?:$|[/?#])')
reMaomiListPageSuffix = re.compile(r'-(\d+)\.html?$')
MAOMI_SITE_ORIGIN = 'https://exex.j8olo.cc'

class VideoParse(BaseParse):

    def run(self):
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        chs = self.videoChannel()
        for item in chs:
            ops.inertVideoChannel(item)
        print 'se8 video -- channel ok;,len=',len(chs)
        dbVPN.commit()
        dbVPN.close()
        for item in chs:
            try:
                channelType = item['channelType']
                base_url = item['url']
                if self._is_topic_list_url(base_url):
                    print item['name'], u'专题, 只拉取 1 次 (topic/detail)'
                    con = self.videoParse(
                        item['channel'], base_url, channelType)
                    if con is False:
                        print '专题无数据', item['name'], base_url
                    else:
                        print '专题完成', item['name']
                    continue
                last_page = self._maomi_list_last_page(base_url)
                if last_page:
                    print item['name'], 'list API last_page=', last_page
                else:
                    print item['name'], u'未拿到 last_page, 无数据即停'
                page_end = maxVideoPage
                if last_page and last_page + 1 < page_end:
                    page_end = last_page + 1
                for i in range(1, page_end):
                    page_url = self._list_page_url(base_url, i)
                    con = self.videoParse(
                        item['channel'], page_url, channelType)
                    if con is False:
                        print '没有数据了啊-======页数', i, '---', item['name'], page_url
                        break
                    print '解析页数 ', item['name'], page_url, ' ---', i, '完成'
            except Exception as e:
                print common.format_exception(e)

    def _is_topic_list_url(self, url):
        path = self._url_path_only(url).lower()
        return path.find('/page/topic/') >= 0

    def _list_page_url(self, base_url, page):
        """列表页 URL 不变路径，页码走 ?page=（对应 API list/base-*-*-{page}.js）。"""
        base_url = (base_url or '').strip()
        base_url = base_url.split('?')[0].split('#')[0]
        base_url = reMaomiListPageSuffix.sub('', base_url)
        if page <= 1:
            return base_url
        return '%s?page=%d' % (base_url.rstrip('/'), page)

    def _maomi_list_last_page(self, list_url):
        spec = self._maomi_parse_list_page(list_url)
        if spec is None or spec.get('single_id'):
            return None
        list_channel = spec['list_channel']
        if list_channel == 'topic':
            return 1
        list_name = self._maomi_resolve_list_name(
            list_channel, spec['list_name'] or list_channel)
        payload = self._maomi_fetch_list_payload(
            list_channel, list_name, 1)
        if not payload:
            return None
        meta = payload.get('list') or {}
        last_page = meta.get('last_page')
        if last_page:
            return int(last_page)
        return None

    def videoChannel(self):
        channelList = []
        for ahref in self.header():
            href = (ahref.get('href') or '').strip()
            if href.count('/page/') == 0:
                continue
            name = (ahref.text or '').strip()
            if not name:
                continue
            obj = {}
            obj['name'] = name
            obj['url'] = href
            obj['baseurl'] = baseurl
            obj['updateTime'] = datetime.datetime.now()
            obj['pic'] = ''
            obj['rate'] = 1.2
            obj['channel'] = 'miaomi' + name
            obj['showType'] = 3
            obj['channelType'] = 'miaomi_all'
            channelList.append(obj)
        print 'se8 videoChannel from header.html, len=', len(channelList)
        return channelList
    def nvviderPaser(self, channel, url):
        soup = self.fetchUrl(url)
        div = soup.first("div", {"class": "text-list-html "})
        if div!=None:
            lis = div.findAll('li')
            if len(lis)==0:
                return False
            for li in lis:
                ahref = li.first('a')
                if ahref != None:
                    for i in range(1, 10):
                        try:
                            print '解析女优频道',channel,ahref.get('href'),ahref.get('title'),i
                            url = ahref.get('href')
                            if i!=1:
                                url = "%s%s%s"%(ahref.replace(".html", "-"),i,".html")
                            self.videoParse(channel, url)
                        except Exception as e:
                            pass
            return True
    def videoParse(self, channel, url, channelType):
        dataList = []
        maomi_rows = self._maomi_video_list_rows(url)
        if maomi_rows is not None:
            for row in maomi_rows:
                fields = self._maomi_row_fields(row)
                if fields is None:
                    continue
                obj = {}
                obj['url'] = fields['url']
                obj['pic'] = fields['pic']
                obj['name'] = fields['name']
                obj['path'] = fields['path']
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                obj['baseurl'] = baseurl
                print channel, obj['name'], obj['url'], obj['pic']
                dataList.append(obj)
        else:
            for fields in self._video_list_from_legacy_html(url):
                obj = {}
                obj['url'] = fields['url']
                obj['pic'] = fields['pic']
                obj['name'] = fields['name']
                obj['path'] = fields['path']
                obj['updateTime'] = datetime.datetime.now()
                obj['channel'] = channel
                obj['baseurl'] = baseurl
                print channel, obj['name'], obj['url'], obj['pic']
                dataList.append(obj)
        if len(dataList) == 0:
            return False
        dbVPN = db.DbVPN()
        ops = db_ops.DbOps(dbVPN)
        ok, fail = 0, 0
        for obj in dataList:
            if not (obj.get('path') or '').strip():
                print 'skip inertVideo empty path:', obj.get('name'), url
                fail += 1
                continue
            r = ops.inertVideo(obj, 'normal', baseurl, channelType)
            if r is None:
                fail += 1
            else:
                ok += 1
        if fail:
            print 'se8 inertVideo fail=', fail, 'ok=', ok, 'channel=', channel, url
        print 'se8 video -- ; channel =', channel, '; len=', len(dataList), url
        dbVPN.commit()
        dbVPN.close()
        return True

    def _video_list_from_legacy_html(self, url):
        dataList = []
        soup = self.fetchUrl(url)
        div = soup.first("div", {"class": "text-list-html "})
        if div is None:
            return dataList
        lis = div.findAll('li')
        for li in lis:
            ahref = li.first('a')
            if ahref is None:
                continue
            href = ahref.get("href")
            mp4Url = self.parseDomVideo(href)
            if mp4Url is None:
                print 'MP4url', href
                continue
            pic = ''
            img = li.first("img")
            if img is not None:
                if img.get("data-original") is None:
                    src = img.get('src') or ''
                    if src.count("http") > 0:
                        pic = src
                    else:
                        pic = baseurl + src
                else:
                    pic = img.get('data-original')
            dataList.append({
                'url': mp4Url,
                'pic': pic,
                'name': ahref.get("title") or '',
                'path': href or '',
            })
        return dataList

    def _url_path_only(self, url):
        if not url:
            return ''
        if url.startswith('http://') or url.startswith('https://'):
            return urlparse(url).path or ''
        return url.split('?')[0]

    def _maomi_parse_list_page(self, url):
        post_id = self._maomi_post_id(url)
        if post_id:
            return {'single_id': post_id, 'list_channel': None,
                    'list_name': None, 'page': 1}
        page = 1
        raw = url or ''
        if raw.startswith('http://') or raw.startswith('https://'):
            parsed = urlparse(raw)
            qs = parse_qs(parsed.query)
            if qs.get('page'):
                try:
                    page = max(1, int(qs['page'][0]))
                except Exception:
                    pass
            path = parsed.path or ''
        else:
            if '?' in raw:
                qs = parse_qs(raw.split('?', 1)[1])
                if qs.get('page'):
                    try:
                        page = max(1, int(qs['page'][0]))
                    except Exception:
                        pass
            path = raw.split('?')[0].split('#')[0]
        page_match = reMaomiListPageSuffix.search(path)
        if page_match:
            page = int(page_match.group(1))
            path = reMaomiListPageSuffix.sub('', path)
        list_match = reMaomiListPath.search(path)
        if list_match:
            return {
                'single_id': None,
                'list_channel': list_match.group(1),
                'list_name': list_match.group(2),
                'page': page,
            }
        path = path.rstrip('/')
        if path.endswith('/s/video') or path.endswith('/video'):
            return {
                'single_id': None,
                'list_channel': 'remen',
                'list_name': 'remen',
                'page': page,
            }
        parts = [p for p in path.split('/') if p]
        if len(parts) >= 3 and parts[-1].isdigit() and parts[-3] == 's' and parts[-2] == 'video':
            return {'single_id': parts[-1], 'list_channel': None,
                    'list_name': None, 'page': 1}
        if len(parts) >= 2 and parts[-1].isdigit() and parts[-2] == 'video':
            return {'single_id': parts[-1], 'list_channel': None,
                    'list_name': None, 'page': 1}
        s_video = re.search(r'/s/video/([^/]+)$', path)
        if s_video:
            ch = s_video.group(1)
            return {
                'single_id': None,
                'list_channel': ch,
                'list_name': ch,
                'page': page,
            }
        return None

    def _maomi_list_api_path(self, list_channel, list_name, page):
        return '/data/list/base-%s-%s-%d.js' % (
            list_channel, list_name, page)

    def _maomi_fetch_list_payload(self, list_channel, list_name, page):
        api_path = self._maomi_list_api_path(
            list_channel, list_name, page)
        plain = self._maomi_decrypt_api(api_path)
        if not plain:
            return None
        try:
            return json.loads(plain)
        except Exception:
            return None

    def _maomi_resolve_list_name(self, list_channel, list_name):
        if list_channel == 'topic':
            return list_name
        if not list_name or not re.match(r'^\d+$', str(list_name)):
            return list_name
        index = self._maomi_fetch_list_payload(list_channel, list_channel, 1)
        if not index:
            return list_name
        cat_id = str(list_name)
        for cat in index.get('cat_list') or []:
            if str(cat.get('id')) == cat_id or str(cat.get('cat_id')) == cat_id:
                jump = cat.get('jump_name')
                if jump:
                    return jump
        return list_name

    def _maomi_resolve_topic_id(self, raw_id):
        raw_id = str(raw_id)
        index = self._maomi_fetch_list_payload('topic', 'topic', 1)
        if not index:
            return raw_id
        for cat in index.get('cat_list') or []:
            if str(cat.get('id')) == raw_id or str(cat.get('topic_id')) == raw_id:
                tid = cat.get('topic_id')
                if tid:
                    return str(tid)
        return raw_id

    def _maomi_topic_video_rows(self, topic_id, page):
        if page > 1:
            return []
        api_path = '/data/topic/detail-%s.js' % topic_id
        plain = self._maomi_decrypt_api(api_path)
        if not plain:
            return []
        try:
            obj = json.loads(plain)
        except Exception:
            return []
        inner = obj.get('list') or {}
        raw_list = inner.get('list') or {}
        rows = []
        if isinstance(raw_list, dict):
            keys = [k for k in raw_list.keys() if str(k).isdigit()]
            keys.sort(key=lambda x: int(x))
            for k in keys:
                row = raw_list[k]
                if row:
                    rows.append(row)
        elif isinstance(raw_list, list):
            rows = [r for r in raw_list if r]
        for row in rows:
            vid = row.get('id')
            ch = row.get('channel') or 'remen'
            if vid:
                row['_detail_url'] = self._maomi_detail_url(ch, vid)
        return rows

    def _maomi_list_slug_from_url(self, url):
        path = self._url_path_only(url)
        m = re.search(r'/s/video/([^/]+)/\d+', path)
        if m:
            return m.group(1)
        m = reMaomiListPath.search(path)
        if m:
            return m.group(1)
        return 'remen'

    def _maomi_video_list_rows(self, url):
        spec = self._maomi_parse_list_page(url)
        if spec is None:
            return None
        if spec.get('single_id'):
            list_slug = self._maomi_list_slug_from_url(url)
            return [{
                'id': int(spec['single_id']),
                'title': '',
                'thumb': '',
                'video_url': '',
                '_detail_url': self._maomi_detail_url(
                    list_slug, spec['single_id']),
            }]
        list_channel = spec['list_channel']
        if not list_channel:
            return []
        list_name = spec['list_name'] or list_channel
        page = spec['page']
        if list_channel == 'topic':
            topic_id = self._maomi_resolve_topic_id(list_name)
            return self._maomi_topic_video_rows(topic_id, page)
        list_name = self._maomi_resolve_list_name(list_channel, list_name)
        payload = self._maomi_fetch_list_payload(
            list_channel, list_name, page)
        if payload is None:
            return []
        rows = (payload.get('list') or {}).get('data') or []
        if len(rows) == 0 and list_name == list_channel:
            for cat in payload.get('cat_list') or []:
                jump = cat.get('jump_name')
                if not jump or jump == list_name:
                    continue
                payload = self._maomi_fetch_list_payload(
                    list_channel, jump, page)
                if payload is None:
                    continue
                rows = (payload.get('list') or {}).get('data') or []
                if len(rows) > 0:
                    list_name = jump
                    break
        for row in rows:
            vid = row.get('id')
            ch = row.get('channel') or list_channel
            if vid:
                row['_detail_url'] = self._maomi_detail_url(ch, vid)
        return rows

    def _maomi_detail_url(self, list_channel, post_id):
        return '%s/s/video/%s/%s' % (
            MAOMI_SITE_ORIGIN, list_channel, post_id)

    def _maomi_media_url(self, path):
        if not path:
            return ''
        path = path.replace('\\/', '/')
        if path.startswith('http://') or path.startswith('https://'):
            return path
        if not path.startswith('/'):
            path = '/' + path
        path = re.sub(r'/+', '/', path)
        return MAOMI_VIDEO_HOST.rstrip('/') + path

    def _maomi_row_fields(self, row):
        """解析单条列表行；不含 channel（由 videoParse 传入参数写入）。"""
        detail_url = row.get('_detail_url')
        video_path = row.get('video_url') or ''
        if video_path:
            mp4Url = self._maomi_sign_path(
                video_path.replace('\\/', '/'))
        elif detail_url:
            mp4Url = self.parseDomVideo(detail_url)
        else:
            mp4Url = None
        if mp4Url is None:
            print 'MP4url', detail_url or video_path
            return None
        thumb = row.get('thumb') or row.get('thumb_ori') or ''
        name = row.get('title') or row.get('name') or ''
        pic = self._maomi_media_url(thumb)
        if not detail_url:
            vid = row.get('id')
            api_ch = row.get('channel') or 'remen'
            if vid:
                detail_url = self._maomi_detail_url(api_ch, vid)
        return {
            'url': mp4Url,
            'pic': pic or '',
            'name': name or '',
            'path': detail_url or '',
        }

    def parseDomVideo(self, url):
        try:
            post_id = self._maomi_post_id(url)
            if post_id:
                maomi = self._maomi_video_from_topic_api(post_id)
                if maomi:
                    return maomi
            soup = self.fetchUrl(url)
            video = self._video_from_playlist(soup)
            if video:
                return video
            return self._video_from_scripts(soup)
        except Exception as e:
            print common.format_exception(e)
            return None

    def _video_from_playlist(self, soup):
        for div in soup.findAll('div', {'id': 'playlist4'}):
            a = div.first('a')
            if a is None:
                continue
            href = a.get('href')
            if not href:
                continue
            child = self.fetchUrl(href)
            video = self._video_from_scripts(child)
            if video:
                return video
        return None

    def _video_from_scripts(self, soup):
        compact_scripts = []
        for s in soup.findAll('script'):
            if s.text:
                compact_scripts.append(s.text.replace(' ', ''))
        for text in compact_scripts:
            match = m3u8regVideo.search(text)
            if match:
                return 'https://s1.cdn-c55291f64e9b0e3a.com%s.m3u8' % match.group(1)
        for text in compact_scripts:
            match = mp4regVideo.search(text)
            if match:
                return 'https://jccfy.com%s.mp4' % match.group(1)
        maomi = self._maomi_from_script_text(''.join(compact_scripts))
        if maomi:
            return maomi
        for s in soup.findAll('script', {'type': 'text/javascript'}):
            match = regVideo.search(s.text)
            if match is None:
                continue
            key = match.group(1).strip()
            base = urlMap.get(key)
            if base:
                return base + str(match.group(2))
        print '没找到mp4'
        return None

    def _maomi_post_id(self, url):
        match = reMaomiPostId.search(url or '')
        if match:
            return match.group(1) or match.group(2)
        return None

    def _maomi_uri_encrypt(self, path):
        return base64.b64encode(MAOMI_URI_PREFIX + path)

    def _maomi_sign_path(self, path, ip='127.0.0.1'):
        if not path.startswith('/'):
            path = '/' + path
        path = re.sub(r'/+', '/', path)
        ws_time = int(time.time()) + 300
        raw = MAOMI_SIGN_KEY + path + str(ws_time)
        ws_secret = hashlib.md5(raw).hexdigest()
        return '%s%s?wsSecret=%s&wsTime=%d&ip=%s' % (
            MAOMI_VIDEO_HOST.rstrip('/'), path, ws_secret, ws_time, ip)

    def _maomi_from_script_text(self, text):
        if not text:
            return None
        match = reMaomiFullUrl.search(text)
        if match:
            return match.group(0)
        match = reMaomiVideoPath.search(text)
        if match:
            return self._maomi_sign_path(match.group(1))
        match = reMaomiVideoUrlJson.search(text)
        if match:
            path = match.group(1).replace('\\/', '/')
            if '.m3u8' in path:
                return self._maomi_sign_path(path)
        return None

    def _maomi_decrypt_api(self, api_path):
        api_url = '%s/%s' % (
            MAOMI_API_HOST.rstrip('/'), self._maomi_uri_encrypt(api_path))
        try:
            proc = subprocess.Popen(
                ['node', '-'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            node_script = '''
var https=require("https");
var CryptoJS;
try{CryptoJS=require("/tmp/package/crypto-js");}catch(e1){
  try{CryptoJS=require("crypto-js");}catch(e2){process.exit(1);}}
var apiUrl=%s;
var key=Buffer.from(%s,"base64").toString("utf8");
var ivBase=Buffer.from(%s,"base64").toString("utf8");
function decrypt(enc,suffix){
  var iv=CryptoJS.enc.Utf8.parse(ivBase+(suffix||""));
  var k=CryptoJS.enc.Utf8.parse(key);
  return CryptoJS.AES.decrypt(enc,k,{iv:iv,mode:CryptoJS.mode.CBC,padding:CryptoJS.pad.Pkcs7}).toString(CryptoJS.enc.Utf8);
}
https.get(apiUrl,{headers:{"User-Agent":"Mozilla/5.0"}},function(res){
  var d="";res.on("data",function(c){d+=c;});
  res.on("end",function(){
    try{
      var body=JSON.parse(d);
      process.stdout.write(decrypt(body.data, body.suffix));
    }catch(e){process.stdout.write("");}
  });
}).on("error",function(){process.stdout.write("");});
''' % (
                json.dumps(api_url),
                json.dumps(MAOMI_AES_KEY_B64),
                json.dumps(MAOMI_AES_IV_B64))
            out, err = proc.communicate(node_script)
            if proc.returncode != 0:
                return None
            return (out or '').strip() or None
        except Exception as e:
            print common.format_exception(e)
        return None

    def _maomi_video_from_topic_api(self, post_id):
        api_path = '/data/topic/play-%s.js' % post_id
        plain = self._maomi_decrypt_api(api_path)
        if not plain:
            return None
        try:
            obj = json.loads(plain)
            src = obj.get('source') or {}
            info = obj.get('info') or {}
            path = src.get('video_url') or info.get('video_url') or ''
            if not path:
                return None
            return self._maomi_sign_path(path.replace('\\/', '/'))
        except Exception as e:
            print common.format_exception(e)
        return None


if __name__ == '__main__':
    videop = VideoParse()
    url = videop.run()
    print url
