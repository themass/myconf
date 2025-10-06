#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
import time
import signal
from bs4 import BeautifulSoup
import sys
import tempfile  # 用于处理大输出

# 解决 Python 2.7 编码问题
reload(sys)
sys.setdefaultencoding('utf-8')

class CurlFetcher(object):
    def __init__(self):
        # 终端可执行的完整 curl 命令
        self.curl_command = '''curl 'https://hsex.men/video-1132154.htm' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'cache-control: no-cache' \
  -b '_ga=GA1.1.562282098.1743184592; __PPU_puid=7372220048289729256; hid=fqon093adrbeju7n89qe4hlh8k; cf_clearance=s2qPvxOG0Cn.CRS1DAeyHg6dZHNh1jqgvBqe2YuNCIs-1759102121-1.2.1.1-GyfAPs69SwqwrD94Dyg8Gt.IWvsS6fE9CMVbVRvdxDoMDxdUtcLg7jK6_ZtO4QsvUHQPLwO1wFwG6km2tFG6EdVMO19rDAOFNwfnhyoYCANQDnODD7hYnqQcKuYqEltLPagdGouWy3Ca8HoiEdV8wVljUoi49MMlPL.XgTJspKHTdxGPg4Ys4RQjyhSWIBAtFt33c4QdQtFxr4h3aJRE61HX1Bp1cIE0J07RxUtUrLFv1pYLb5qW9nlrNTNTuX4a; _ga_ECF2QFGQ9G=GS2.1.s1759071414$o6$g1$t1759071464$j10$l0$h0; UGVyc2lzdFN0b3JhZ2U=%7B%22CAIFRQ%22%3A%22ADXY8AAAAAAAAAABADR6ZgAAAAAAAAABADR6XAAAAAAAAAAB%22%2C%22CAIFRT%22%3A%22ADXY8AAAAABo2hJQADR6ZgAAAABo2hJQADR6XAAAAABo2hJQ%22%7D; bnState_1871751={"impressions":7,"delayStarted":0}' \
  -H 'pragma: no-cache' \
  -H 'priority: u=0, i' \
  -H 'sec-ch-ua: "Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"' \
  -H 'sec-ch-ua-arch: "arm"' \
  -H 'sec-ch-ua-bitness: "64"' \
  -H 'sec-ch-ua-full-version: "137.0.7151.120"' \
  -H 'sec-ch-ua-full-version-list: "Google Chrome";v="137.0.7151.120", "Chromium";v="137.0.7151.120", "Not/A)Brand";v="24.0.0.0"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-model: ""' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-ch-ua-platform-version: "14.3.0"' \
  -H 'sec-fetch-dest: document' \
  -H 'sec-fetch-mode: navigate' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-fetch-user: ?1' \
  -H 'upgrade-insecure-requests: 1' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36' '''

    def _get_terminal_env(self):
        """获取终端环境变量"""
        env = os.environ.copy()
        python_vars = ['PYTHONPATH', 'PYTHONHOME', 'PYTHONSTARTUP', 'PYTHONIOENCODING']
        for var in python_vars:
            if var in env:
                del env[var]
        return env

    def fetch(self, full_url=None):
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            process = None  # 初始化进程变量
            try:
                # print("第%d次尝试（使用终端环境执行）..." % (retry_count + 1))

                # 如果传入了新URL，替换命令中的URL
                curl_cmd = self.curl_command
                if full_url:
                    curl_cmd = curl_cmd.replace("'https://hsex.men/video-1132154.htm'", "'%s'" % full_url)

                # 使用临时文件存储输出，避免大输出导致的缓冲区问题
                with tempfile.TemporaryFile() as stdout_file:
                    # 启动子进程
                    process = subprocess.Popen(
                        ['bash', '-c', curl_cmd],
                        stdout=stdout_file,  # 输出到临时文件
                        stderr=subprocess.PIPE,
                        env=self._get_terminal_env(),
                        shell=False
                    )

                    # 设置超时信号处理
                    def timeout_handler(signum, frame):
                        raise Exception("请求超时（30秒）")

                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(30)  # 30秒超时

                    # 等待进程完成，避免使用communicate()的潜在问题
                    process.wait()
                    signal.alarm(0)  # 取消超时

                    # 读取临时文件中的输出
                    stdout_file.seek(0)
                    stdout = stdout_file.read()
                    stderr = process.stderr.read()

                # 检查执行结果
                if process.returncode != 0:
                    print("curl 执行失败（代码: %d）" % process.returncode)
                    print("错误详情: %s" % stderr)
                    retry_count += 1
                    time.sleep(2)
                    continue

                # 检测是否被Cloudflare拦截
                response = stdout.decode('utf-8', errors='replace')
                if "cloudflare" in response.lower() or "just a moment" in response.lower():
                    print("被Cloudflare拦截，尝试重试...")
                    retry_count += 1
                    time.sleep(5)
                    continue

                # 解析并返回结果
                soup = BeautifulSoup(response, "html.parser", from_encoding="utf-8")
                # print("成功获取页面！")
                return soup

            except Exception as e:
                print("执行错误: %s" % str(e))
                retry_count += 1
                time.sleep(2)
            finally:
                # 确保进程被终止
                if process and process.poll() is None:
                    try:
                        process.kill()
                        print("强制终止未响应的子进程")
                    except:
                        pass

        print("达到最大重试次数，获取失败")
        return None


# 使用示例
if __name__ == "__main__":
    fetcher = CurlFetcher()
    # 可以传入自定义URL
    soup = fetcher.fetch("https://hsex.men/video-1132154.htm")

    if soup and soup.title:
        print("\n页面标题: %s" % soup.title.text)
    else:
        print("\n未获取到有效页面内容")
