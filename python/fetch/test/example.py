#!/usr/bin python
# -*- coding: utf-8 -*-
import urllib2
import cookielib
import time
import random
import ssl
import string
from urllib import quote
import socket

# 强制使用与浏览器一致的TLS版本和加密套件
class TLSAdapter(urllib2.HTTPSHandler):
    def __init__(self):
        urllib2.HTTPSHandler.__init__(self)

    def https_open(self, req):
        # 模拟Chrome的TLS配置
        context = ssl.create_default_context()
        context.set_ciphers('ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384')
        context.options |= ssl.OP_NO_TLSv1
        context.options |= ssl.OP_NO_TLSv1_1
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        def http_class_wrapper(*args, **kwargs):
            args = list(args)
            args[0] = context
            return ssl.wrap_socket(*args,** kwargs)

        old_wrap_socket = socket.ssl
        socket.ssl = http_class_wrapper
        try:
            return urllib2.HTTPSHandler.https_open(self, req)
        finally:
            socket.ssl = old_wrap_socket

def generate_random_string(length=10):
    """生成随机字符串，模拟浏览器生成的临时标识"""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def get_random_user_agent():
    """更丰富的User-Agent池，包含不同浏览器和版本"""
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.6723.60 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
    ]
    return random.choice(user_agents)

def create_headers(referer=None):
    """模拟浏览器完整请求头，包含动态生成的特征值"""
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-arch': '"arm"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-full-version': '"137.0.7151.120"',
        'sec-ch-ua-full-version-list': '"Google Chrome";v="137.0.7151.120", "Chromium";v="137.0.7151.120", "Not/A)Brand";v="24.0.0.0"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"macOS"',
        'sec-ch-ua-platform-version': '"14.3.0"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none' if not referer else 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': get_random_user_agent(),
        'DNT': '1',
        'Sec-GPC': '1',
        # 增加动态生成的客户端标识
        'X-Client-Data': 'ck' + generate_random_string(24) + '='  # 模拟Chrome客户端数据
    }
    if referer:
        headers['referer'] = referer
    return headers

def parse_cookies(cookie_string, domain):
    """更精确的Cookie解析，处理特殊字符和过期时间"""
    cookie_jar = cookielib.LWPCookieJar()
    for cookie in cookie_string.split('; '):
        if '=' not in cookie:
            continue
        name, value = cookie.split('=', 1)
        # 处理URL编码的Cookie值
        try:
            name = quote(name.strip())
            value = quote(value.strip())
        except:
            pass

        # 创建Cookie对象，精确设置属性
        c = cookielib.Cookie(
            version=0,
            name=name,
            value=value,
            port=None,
            port_specified=False,
            domain=domain,
            domain_specified=True,
            domain_initial_dot=False,
            path='/',
            path_specified=True,
            secure=True,
            expires=None,
            discard=False,
            comment=None,
            comment_url=None,
            rest={'HttpOnly': None},  # 模拟HttpOnly属性
            rfc2109=False
        )
        cookie_jar.set_cookie(c)
    return cookie_jar

def fetch_with_enhanced_fingerprint(url, cookie_string, domain, max_retries=3):
    """使用增强的浏览器指纹进行请求"""
    # 生成随机客户端标识，每次请求不同
    client_id = generate_random_string(16)

    for attempt in range(max_retries):
        try:
            # 创建带TLS适配器的opener
            cookie_jar = parse_cookies(cookie_string, domain)
            cookie_handler = urllib2.HTTPCookieProcessor(cookie_jar)
            opener = urllib2.build_opener(TLSAdapter(), cookie_handler)

            # 随机延迟，模拟人类操作节奏
            delay = random.uniform(2.0, 4.0) + (attempt * 1.5)
            print "第%d次尝试，延迟%.2f秒 (客户端标识: %s)" % (attempt + 1, delay, client_id[:8])
            time.sleep(delay)

            # 创建请求
            headers = create_headers()
            req = urllib2.Request(url, headers=headers)

            # 模拟浏览器的请求发送时间间隔（微秒级）
            time.sleep(random.uniform(0.001, 0.005))

            # 发送请求
            response = opener.open(req, timeout=20)

            # 处理gzip压缩（很多服务器要求支持）
            content_encoding = response.headers.getheader('Content-Encoding')
            content = response.read()
            if content_encoding == 'gzip':
                import gzip
                from StringIO import StringIO
                content = gzip.GzipFile(fileobj=StringIO(content)).read()
            elif content_encoding == 'deflate':
                import zlib
                content = zlib.decompress(content)

            # 处理编码
            content_type = response.headers.getheader('Content-Type') or ''
            charset = 'utf-8'
            if 'charset=' in content_type:
                charset = content_type.split('charset=')[1].split(';')[0]

            try:
                content = content.decode(charset)
            except UnicodeDecodeError:
                for encoding in ['gbk', 'gb2312', 'utf-8', 'iso-8859-1']:
                    try:
                        content = content.decode(encoding)
                        break
                    except:
                        continue
                else:
                    content = content.decode('utf-8', errors='ignore')

            print "请求成功，状态码: %s" % response.getcode()
            return content

        except urllib2.HTTPError as e:
            print "HTTP错误: %s，尝试第%d次重试" % (e.code, attempt + 1)
            if e.code == 403:
                # 403时更新Cookie和客户端标识
                cookie_string = refresh_cookie(cookie_string)
                client_id = generate_random_string(16)
                if attempt < max_retries - 1:
                    continue
            break
        except urllib2.URLError as e:
            print "URL错误: %s，尝试第%d次重试" % (e.reason, attempt + 1)
            if attempt < max_retries - 1:
                continue
            break
        except Exception as e:
            print "发生错误: %s，尝试第%d次重试" % (str(e), attempt + 1)
            if attempt < max_retries - 1:
                continue
            break

    print "所有尝试均失败"
    return None

def refresh_cookie(old_cookie):
    """智能刷新Cookie中的动态字段"""
    import datetime
    now = datetime.datetime.now()
    timestamp = int(now.strftime("%s"))

    new_cookie = old_cookie

    # 更新cf_clearance中的时间戳（Cloudflare常见Cookie）
    if 'cf_clearance=' in new_cookie:
        parts = new_cookie.split('cf_clearance=')
        if len(parts) > 1:
            cf_segment = parts[1].split(';')[0]
            cf_parts = cf_segment.split('-')
            if len(cf_parts) >= 5:
                # 替换时间戳部分
                cf_parts[1] = str(timestamp)
                new_cf_segment = '-'.join(cf_parts)
                new_cookie = parts[0] + 'cf_clearance=' + new_cf_segment + ';' + ';'.join(parts[1].split(';')[1:])

    # 更新Google Analytics相关Cookie
    for ga_key in ['_ga=', '_ga_']:
        if ga_key in new_cookie:
            parts = new_cookie.split(ga_key)
            if len(parts) > 1:
                ga_segment = parts[1].split(';')[0]
                # 保留前缀，更新时间戳部分
                if '.' in ga_segment:
                    ga_prefix = '.'.join(ga_segment.split('.')[:2])
                    new_ga_segment = ga_prefix + '.' + str(int(random.random() * 1000))
                    new_cookie = parts[0] + ga_key + new_ga_segment + ';' + ';'.join(parts[1].split(';')[1:])

    return new_cookie

if __name__ == "__main__":
    target_url = "https://hsex.men/"
    domain = "hsex.men"

    # 请在此处替换为浏览器中最新获取的Cookie（F12 -> Network -> 复制完整Cookie）
    cookie_string = '_ga=GA1.1.562282098.1743184592; __PPU_puid=7372220048289729256; hid=1ko1ctu55qpsm0mm73cvfm8mh8; cf_clearance=TIinfpcrEUAcj70jgjq2Vb4wls6l4rP7t4.8QeNcGKY-1754581922-1.2.1.1-0f0DYW_exHmW8pStg.GR9F.BFIHh_idQ9NQSo.KNGn23P_f9I1EmBmDenezu06s55dwEbH4VIlJ1rb6PPdT4zYnKSrBfflIEQk5F_Y_zL71wTZURcM.U_u_.TGqxMTXbXBw4urI_4T6j6asKip7L4dw.UkZuPXf2.ESUz.3L_pG9vtcmq.RoPskn8HOV8VzlaR1OWgqs53OJ_XVTUoisM2GQmQhJ.lPq6du361ZlE_8; UGVyc2lzdFN0b3JhZ2U=%7B%22CAIFRQ%22%3A%22ADR6ZgAAAAAAAAAE%22%2C%22CAIFRT%22%3A%22ADR6ZgAAAABolYRQ%22%7D; bnState_1871751={"impressions":4,"delayStarted":0}; _ga_ECF2QFGQ9G=GS2.1.s1754581918$o4$g1$t1754582074$j54$l0$h0'

    # 获取网页内容
    content = fetch_with_enhanced_fingerprint(target_url, cookie_string, domain)

    if content:
        print "\n网页内容长度: %d" % len(content)
        print "\n网页内容预览:"
        print content[:1000]

