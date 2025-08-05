#!/usr/bin python
# -*- coding: utf-8 -*-
import re,sys
reload(sys)
sys.setdefaultencoding('utf8')
# 两段独立的字符串
text1 = '<script>var playUrl="//"+play+"/movie-hls/170430/ydgzy23/index.m3u8";var posterImg="https://pppp.642p.com/201704/30/ydgzy23.jpg";</script>'
text2 = '<script>var playUrl="//"+javplay+"/videos/202407/668ec3198eb67eee93c91775/hls/index.m3u8";var posterImg="https://pppp.642p.com/images/202407/668ec3198eb67eee93c91775/cover.txt";</script>'

#修正后的正则表达式：
# 1. 使用原始字符串 (r'...')
# 2. 明确匹配双引号和斜杠
# 3. 使用非贪婪匹配确保只捕获到第一个 .m3u8
pattern = r'var playUrl=(\'|\")//(\'|\")\+[^+]+\+(\'|\")(/.*?\.m3u8)(\'|\")'

# 分别处理每段字符串
def extract_path(text):
    match = re.search(pattern, text)
    if match:
        # 第4个捕获组包含路径部分
        return match.group(4)
    return None

# 提取并打印每个字符串的路径
path1 = extract_path(text1)
path2 = extract_path(text2)

print path1
print path2