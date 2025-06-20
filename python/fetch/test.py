#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

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

def js_to_python(p, a, c, k, e, d):
    """将JavaScript混淆代码转换为Python可执行代码（Python 2.7兼容）"""
    def e_func(c):
        return base36encode(c)

    # 创建替换字典
    for idx in range(c):
        key = base36encode(idx)
        d[key] = k[idx] if idx < len(k) and k[idx] else key

    # 执行变量替换（使用Python 2.7兼容的字符串格式化）
    for idx in range(c):
        if idx < len(k) and k[idx]:
            # 使用原始字符串 + % 格式化替代 f-string
            pattern = r'\b%s\b' % e_func(idx)
            p = re.sub(pattern, k[idx], p)

    return p

def parserText(text):
    """解析混淆的JavaScript代码并提取视频URL"""
    # 匹配eval混淆代码的正则表达式
    eval_pattern = r"eval\(function\(p,a,c,k,e,d\)\{.*?\}\('(.*?)',(\d+),(\d+),'(.*?)'\.split\('\|'\),(\d+),\{\}\)\)"
    match = re.search(eval_pattern, text)

    if not match:
        return None

    # 提取混淆参数
    p = match.group(1)
    a = int(match.group(2))
    c = int(match.group(3))
    k_list = match.group(4)
    k = k_list.split('|') if k_list else []
    e = int(match.group(5))
    d = {}

    # 解码JavaScript混淆代码
    try:
        decoded_code = js_to_python(p, a, c, k, e, d)
    except Exception as e:
        print("解码失败: %s" % str(e))
        return None

    # 提取视频URL（Python 2.7兼容的正则表达式）
    url_pattern = r'(https?://[^"\';\s<>\[\]]+\.(?:m3u8|mp4|avi|flv|mov|wmv))'
    urls = re.findall(url_pattern, decoded_code)

    if urls:
        return urls[0]

    # 如果没有直接匹配到完整URL，尝试提取部分URL
    partial_url_pattern = r'(https?://[^"\';\s<>\[\]]+)'
    partial_urls = re.findall(partial_url_pattern, decoded_code)

    for url in partial_urls:
        if '.m3u8' in url:
            # 清理URL，确保以.m3u8结尾
            clean_url = url.split('?')[0].split('#')[0]
            if not clean_url.endswith('.m3u8'):
                # 寻找最后一个点并添加.m3u8
                last_dot = clean_url.rfind('.')
                if last_dot != -1:
                    clean_url = clean_url[:last_dot] + '.m3u8'
                else:
                    clean_url += '.m3u8'
            return clean_url

    return None

# 示例使用（Python 2.7兼容）
if __name__ == "__main__":
    # 测试用例1：包含m3u8的混淆代码
    obfuscated_js = """
                eval(function(p,a,c,k,e,d){e=function(c){return c.toString(36)};if(!''.replace(/^/,String)){while(c--){d[c.toString(a)]=k[c]||c.toString(a)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('u(![\'m\'+\'i\'+\'s\'+\'s\'+\'a\'+\'v\'+\'8\'+\'8\'+\'8\'+\'.\'+\'c\'+\'o\'+\'m\',\'1\'+\'2\'+\'3\'+\'a\'+\'v\'+\'.\'+\'o\'+\'r\'+\'g\',\'m\'+\'i\'+\'s\'+\'s\'+\'a\'+\'v\'+\'.\'+\'l\'+\'i\'+\'v\'+\'e\',\'k\'+\'i\'+\'d\'+\'d\'+\'e\'+\'w\'+\'.\'+\'c\'+\'o\'+\'m\',\'m\'+\'i\'+\'s\'+\'s\'+\'a\'+\'v\'+\'7\'+\'8\'+\'9\'+\'.\'+\'c\'+\'o\'+\'m\',\'t\'+\'h\'+\'i\'+\'s\'+\'a\'+\'v\'+\'2\'+\'.\'+\'c\'+\'o\'+\'m\',\'m\'+\'i\'+\'s\'+\'s\'+\'a\'+\'v\'+\'0\'+\'1\'+\'.\'+\'c\'+\'o\'+\'m\',\'m\'+\'i\'+\'s\'+\'s\'+\'a\'+\'v\'+\'1\'+\'2\'+\'3\'+\'.\'+\'c\'+\'o\'+\'m\',\'m\'+\'i\'+\'s\'+\'s\'+\'a\'+\'v\'+\'.\'+\'w\'+\'s\',\'m\'+\'i\'+\'s\'+\'s\'+\'a\'+\'v\'+\'.\'+\'a\'+\'i\',\'m\'+\'.\'+\'t\'+\'h\'+\'i\'+\'s\'+\'.\'+\'a\'+\'v\',\'n\'+\'j\'+\'a\'+\'v\'+\'t\'+\'v\'+\'.\'+\'c\'+\'o\'+\'m\',\'m\'+\'q\'+\'a\'+\'v\'+\'.\'+\'c\'+\'o\'+\'m\'].p(5.4.6)){5.4.b=5.4.b.f(5.4.6,\'m\'+\'i\'+\'s\'+\'s\'+\'a\'+\'v\'+\'.\'+\'a\'+\'i\')}',33,33,'||||location|window|host|||||href||z||replace||||||||||includes|y||||if||'.split('|'),0,{}))
    """

    # 测试用例2：域名跳转混淆代码
    domain_redirect_js = """
    eval(function(p,a,c,k,e,d){e=function(c){return c.toString(36)};if(!''.replace(/^/,String)){while(c--){d[c.toString(a)]=k[c]||c.toString(a)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('u(![\'m\'+\'i\'+\'s\'+\'s\'+\'a\'+\'v\'+\'.\'+\'a\'+\'i\',\'m\'+\'i\'+\'s\'+\'s\'+\'a\'+\'v\'+\'7\'+\'8\'+\'9\'+\'.\'+\'c\'+\'o\'+\'m\'].p(5.4.6)){5.4.b=5.4.b.f(5.4.6,\'m\'+\'i\'+\'s\'+\'s\'+\'a\'+\'v\'+\'.\'+\'a\'+\'i\')}',33,33,'||||location|window|host|||||href||z||replace||||||||||includes|y||||if||'.split('|'),0,{}))
    """

    print "测试用例1结果:", parserText(obfuscated_js)
    print "测试用例2结果:", parserText(domain_redirect_js)