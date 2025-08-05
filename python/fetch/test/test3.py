#!/usr/bin python
# -*- coding: utf-8 -*-
import threading
import urllib2
import ssl
import socket
import zlib
import time
from bs4 import BeautifulSoup

class BaseParse(object):
    """基础解析类"""
    def __init__(self):
        self.fetcher = None

class VideoParse(BaseParse, threading.Thread):
    """视频解析类，继承基础解析类并实现多线程功能"""
    def __init__(self, video_url=None):
        BaseParse.__init__(self)
        threading.Thread.__init__(self)

        self.video_url = video_url
        self.result = None
        self.is_running = False

        # 初始化SSL上下文（修复兼容性问题）
        self._init_ssl_context()

        # 模拟浏览器请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.google.com/'
        }

    def _init_ssl_context(self):
        """初始化SSL上下文，支持更多协议和选项"""
        # 创建不验证证书的上下文
        self.ssl_ctx = ssl.create_default_context()
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.verify_mode = ssl.CERT_NONE

        # 启用TLSv1.0和TLSv1.1（兼容旧服务器）
        self.ssl_ctx.options &= ~ssl.OP_NO_TLSv1
        self.ssl_ctx.options &= ~ssl.OP_NO_TLSv1_1

        # 禁用压缩（避免CRIME攻击相关问题）
        self.ssl_ctx.options |= ssl.OP_NO_COMPRESSION

        # 移除不兼容的属性设置
        # self.ssl_ctx.session_cache_mode = ssl.SESSION_CACHE_OFF  # Python 2.7不支持

    def run(self):
        """线程执行的主函数"""
        self.is_running = True
        try:
            if not self.video_url:
                raise ValueError("未设置视频URL")

            # 抓取并解析页面
            content = self._fetch_with_retry()
            if content:
                self.result = self._parse_content(content)
            else:
                self.result = {"status": "失败", "message": "无法获取页面内容"}

        except Exception as e:
            self.result = {"status": "错误", "message": str(e)}
        finally:
            self.is_running = False

    def _fetch_with_retry(self):
        """带重试机制的页面抓取方法"""
        max_retries = 5
        for attempt in xrange(max_retries):
            try:
                # 创建请求对象
                req = urllib2.Request(self.video_url, headers=self.headers)

                # 设置超时并打开URL
                socket.setdefaulttimeout(30)
                response = urllib2.urlopen(req, timeout=30, context=self.ssl_ctx)

                # 获取响应内容
                content_encoding = response.headers.getheader('Content-Encoding', '')
                content = response.read()

                # 处理gzip压缩内容
                if 'gzip' in content_encoding.lower():
                    content = zlib.decompress(content, 16 + zlib.MAX_WBITS)
                print content
                return content

            except ssl.SSLError as e:
                print "SSL错误 ({0}/{1}): {2} - {3}".format(
                    attempt+1, max_retries, self.video_url, str(e))

                # 针对特定错误尝试不同的SSL上下文
                if 'KRB5_S_TKT_NYV' in str(e) or 'unexpected eof' in str(e).lower():
                    # 尝试更宽松的上下文
                    self.ssl_ctx = ssl._create_unverified_context()

            except (urllib2.URLError, socket.timeout) as e:
                print "网络错误 ({0}/{1}): {2} - {3}".format(
                    attempt+1, max_retries, self.video_url, str(e))

            except Exception as e:
                print "其他错误 ({0}/{1}): {2} - {3}".format(
                    attempt+1, max_retries, self.video_url, str(e))

            # 指数退避重试
            wait_time = 2 ** attempt
            print "等待 {0} 秒后重试...".format(wait_time)
            time.sleep(wait_time)

        print "达到最大重试次数，无法获取: {0}".format(self.video_url)
        return None

    def _parse_content(self, content):
        """解析HTML内容，提取视频信息"""
        if not content:
            return {"status": "失败", "message": "无内容可解析"}

        try:
            # 创建BeautifulSoup对象
            soup = BeautifulSoup(content, 'html.parser')

            # 这里需要根据实际页面结构编写解析逻辑
            # 以下是示例代码，需根据目标网站调整

            # 提取标题
            title = soup.title.text if soup.title else "未找到标题"

            # 提取视频URL（示例逻辑，需根据实际页面修改）
            video_url = None
            video_tags = soup.find_all('video')
            if video_tags:
                video_url = video_tags[0].get('src')

            if not video_url:
                # 尝试从script标签中提取
                script_tags = soup.find_all('script')
                for script in script_tags:
                    script_text = script.get_text()
                    if 'playUrl' in script_text:
                        # 使用正则表达式提取playUrl
                        import re
                        match = re.search(r'var playUrl="([^"]+)"', script_text)
                        if match:
                            video_url = match.group(1)
                            # 处理playUrl中的变量拼接
                            if '"+iplay+"' in video_url:
                                video_url = video_url.replace('"+iplay+"', '')

            return {
                "status": "成功",
                "title": title,
                "video_url": video_url,
                "original_url": self.video_url,
                "content_length": len(content)
            }

        except Exception as e:
            return {"status": "解析错误", "message": str(e)}


# 使用示例
if __name__ == "__main__":
    # 创建并启动解析线程
    parser = VideoParse(video_url="https://c4441.com/video/zipai/index.html")
    parser.start()

    # 等待线程完成
    parser.join()

    # 输出结果
    print "解析结果:"
    for key, value in parser.result.items():
        print "  {0}: {1}".format(key, value)