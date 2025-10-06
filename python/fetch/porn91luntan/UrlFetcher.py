#!/usr/bin python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import time,sys
import subprocess
import signal
reload(sys)
sys.setdefaultencoding('utf8')
class UrlFetcher(object):
    def __init__(self, chromedriver_path=None):
        # 配置浏览器选项
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")

        # 手动手动 ChromeDriver 路径（可手动指定）
        self.chromedriver_path = chromedriver_path

        # 初始化参数
        self.driver = None
        self.max_retries = 3
        self.cookie_update_interval = 300
        self.last_cookie_update = 0
        self.default_cookies = "CzG_fid21=1758821945; _ga=GA1.1.350018691.1758817990; CzG_sid=970t7K; utf8tt=26fcQWmwproJKgagzOxlq96xuT70iojHhiA%2BQ80L; CzG_fid33=1758822882; CzG_fid4=1758822442; CzG_oldtopics=D783537D783574D783517D783571D783451D781758D783555D783562D783582D783577D783587D; CzG_visitedfid=21D4D11D36D34D33; _ga_LTGT8CMVLT=GS2.1.s1758817990$o1$g1$t1758818913$j60$l0$h0; cf_clearance=brZ0We_5rG18oOz4ESqIr7bL68eAHdmHviHTkIgOE7E-1758818913-1.2.1.1-mJHYGIn7Z5kqIAzTHxBhhM2BbCD8XK99BRe7_ziT4hu48BeW6ns2QgNtTY3iZaPbsMSbHXnUWrI1f1yiE6.EeI5l41afGzqcuUgdB.p64b1UzJK5e9z5GkKL9ap8kUYVtqazWflsHl171mHBCwqw1wCRo7E29_IF2ZH7lZjYpFdlZ0R9adGKg7yQZ9VhBAlz6t13DJNreCoxm9c83HjP87ymcNDr25X2Y2cY0GQ4XtU"

    def __del__(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

    def _init_driver(self):
        """初始化浏览器驱动，支持手动指定路径"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

        try:
            # 根据是否指定路径选择不同的初始化方式
            if self.chromedriver_path:
                self.driver = webdriver.Chrome(
                    executable_path=self.chromedriver_path,
                    chrome_options=self.chrome_options
                )
            else:
                self.driver = webdriver.Chrome(
                    chrome_options=self.chrome_options
                )

            self.driver.set_page_load_timeout(30)
            self.driver.set_script_timeout(30)
            return True
        except Exception as e:
            print("初始化浏览器驱动失败: %s" % str(e))
            self.driver = None
            return False

    def _is_cloudflare_challenge(self, content):
        if not content:
            return False
        content_lower = content.lower()
        return "cloudflare" in content_lower or "just a moment" in content_lower or "enable javascript and cookies to continue" in content_lower

    def _update_cookies(self):
        if not self.driver:
            if not self._init_driver():
                return None

        try:
            self.driver.get("https://t0908.9p47p.com/")
            time.sleep(5)

            # 尝试处理可能的验证按钮
            try:
                verify_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='button'][value*='Verify']"))
                )
                verify_button.click()
                time.sleep(5)
            except:
                pass

            cookies = self.driver.get_cookies()
            cookie_str = "; ".join(["%s=%s" % (c['name'], c['value']) for c in cookies])
            self.last_cookie_update = time.time()
            return cookie_str
        except Exception as e:
            print("更新 Cookie 失败: %s" % str(e))
            return None

    def fetch_with_selenium(self, url):
        if not self.driver and not self._init_driver():
            return None

        try:
            self.driver.get(url)

            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            time.sleep(1)
            page_source = self.driver.page_source

            if self._is_cloudflare_challenge(page_source):
                print("检测到 Cloudflare 验证，等待验证完成...")
                # 关闭无头模式时可以手动完成验证
                time.sleep(1)
                page_source = self.driver.page_source

                if self._is_cloudflare_challenge(page_source):
                    self.driver.refresh()
                    time.sleep(1)
                    page_source = self.driver.page_source

            return page_source

        except TimeoutException:
            print("访问 %s 超时" % url)
            return self.driver.page_source if self.driver else None
        except WebDriverException as e:
            print("Selenium 错误: %s" % str(e))
            self._init_driver()
            return None

    def fetch_with_curl(self, url, cookies=None):
        if not cookies or (time.time() - self.last_cookie_update) > self.cookie_update_interval:
            cookies = self._update_cookies()
            if not cookies:
                print("使用默认 Cookie")
                cookies = self.default_cookies

        curl_command = [
            'curl', url,
            '-H', 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            '-H', 'accept-language: zh-CN,zh;q=0.9',
            '-H', 'cache-control: no-cache',
            '-b', cookies,
            '-H', 'pragma: no-cache',
            '-H', 'sec-ch-ua: "Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            '-H', 'sec-ch-ua-mobile: ?0',
            '-H', 'sec-ch-ua-platform: "macOS"',
            '-H', 'sec-fetch-dest: document',
            '-H', 'sec-fetch-mode: navigate',
            '-H', 'sec-fetch-site: none',
            '-H', 'sec-fetch-user: ?1',
            '-H', 'upgrade-insecure-requests: 1',
            '-H', 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            '--compressed',
            '--insecure'
        ]

        try:
            process = subprocess.Popen(
                curl_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Python 2.7 超时处理
            def timeout_handler(signum, frame):
                raise Exception("curl 请求超时")

            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)

            stdout, stderr = process.communicate()
            signal.alarm(0)

            if process.returncode != 0:
                print("curl 错误 (代码 %d): %s" % (process.returncode, stderr))

            return stdout
        except Exception as e:
            if "超时" in str(e):
                print("curl 请求超时")
                try:
                    process.kill()
                except:
                    pass
            else:
                print("curl 执行异常: %s" % str(e))
            return None

    def fetchUrl(self, url):
        retry_count = 0

        while retry_count < self.max_retries:
            try:
                page_content = self.fetch_with_selenium(url)

                if not page_content or self._is_cloudflare_challenge(page_content):
                    print("尝试使用 curl 获取页面...")
                    page_content = self.fetch_with_curl(url)

                if not page_content:
                    raise Exception("未获取到页面内容")

                if self._is_cloudflare_challenge(page_content):
                    raise Exception("Cloudflare 验证未通过")

                soup = BeautifulSoup(page_content)
                return soup

            except Exception as e:
                print("获取页面错误: %s" % str(e))
                print("重试 %s，次数: %d" % (url, retry_count))
                retry_count += 1
                time.sleep(2)

        print("达到最大重试次数，获取 %s 失败" % url)
        return BeautifulSoup('')

# 使用示例 - 手动指定 ChromeDriver 路径
if __name__ == "__main__":
    # 请替换为你的 ChromeDriver 实际路径
    # Windows 示例: "C:/tools/chromedriver.exe"
    # macOS/Linux 示例: "/usr/local/bin/chromedriver"
    chromedriver_path = "/usr/local/bin/chromedriver"

    fetcher = UrlFetcher(chromedriver_path=chromedriver_path)
    url = "https://t0908.9p47p.com/forumdisplay.php?fid=21&page=1"
    soup = fetcher.fetchUrl(url)
    print("获取到的页面标题: %s" % soup.title.text if soup.title else "未获取到标题")
