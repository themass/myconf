#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JavaScript Packer解码器
专门用于解码JavaScript packer加密的代码
"""

import re
import base64
import urllib2

class JavaScriptPackerDecoder(object):
    def __init__(self):
        self.decoded_results = []
    
    def decode_packer(self, js_code):
        """解码JavaScript packer"""
        try:
            # 查找eval(function(p,a,c,k,e,d){...})模式
            packer_pattern = r'eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*d\s*\)\s*\{[^}]*\}\s*\(([^)]+)\)\s*\)'
            
            match = re.search(packer_pattern, js_code, re.DOTALL | re.IGNORECASE)
            if not match:
                return None
            
            params_str = match.group(1)
            return self.decode_packer_params(params_str)
            
        except Exception as e:
            print "Error decoding packer: %s" % e
            return None
    
    def decode_packer_params(self, params_str):
        """解码packer参数"""
        try:
            # 分割参数
            parts = params_str.split("','")
            
            if len(parts) < 4:
                return None
            
            # 提取各个部分
            code_part = parts[0].strip("'")
            strings_part = parts[1].strip("'")
            numbers_part = parts[2].strip("'")
            base_part = parts[3].strip("'")
            
            # 解析字符串数组
            strings = self.parse_string_array(strings_part)
            if not strings:
                return None
            
            # 解析数字数组
            numbers = self.parse_number_array(numbers_part)
            
            # 解析基数
            base = int(base_part) if base_part.isdigit() else 36
            
            # 解码代码
            decoded_code = self.decode_with_strings(code_part, strings, numbers, base)
            
            return {
                'original_code': code_part,
                'strings': strings,
                'numbers': numbers,
                'base': base,
                'decoded_code': decoded_code
            }
            
        except Exception as e:
            print "Error decoding packer params: %s" % e
            return None
    
    def parse_string_array(self, array_str):
        """解析字符串数组"""
        try:
            # 移除方括号
            array_str = array_str.strip('[]')
            
            # 分割字符串
            strings = []
            current = ""
            in_quotes = False
            quote_char = None
            
            for char in array_str:
                if char in ['"', "'"] and not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char and in_quotes:
                    in_quotes = False
                    if current:
                        strings.append(current)
                        current = ""
                elif in_quotes:
                    current += char
                elif char == ',' and not in_quotes:
                    if current.strip():
                        strings.append(current.strip())
                        current = ""
                elif not in_quotes:
                    current += char
            
            if current.strip():
                strings.append(current.strip())
            
            return strings
            
        except Exception as e:
            print "Error parsing string array: %s" % e
            return None
    
    def parse_number_array(self, array_str):
        """解析数字数组"""
        try:
            # 移除方括号
            array_str = array_str.strip('[]')
            
            # 分割数字
            numbers = []
            for num_str in array_str.split(','):
                num_str = num_str.strip()
                if num_str.isdigit():
                    numbers.append(int(num_str))
            
            return numbers
            
        except Exception as e:
            print "Error parsing number array: %s" % e
            return []
    
    def decode_with_strings(self, code, strings, numbers, base):
        """使用字符串数组解码代码"""
        try:
            decoded = code
            
            # 替换字符串引用
            for i, string in enumerate(strings):
                pattern = r'\b' + str(i) + r'\b'
                decoded = re.sub(pattern, '"' + string + '"', decoded)
            
            # 替换数字引用
            for i, number in enumerate(numbers):
                pattern = r'\b' + str(i) + r'\b'
                decoded = re.sub(pattern, str(number), decoded)
            
            return decoded
            
        except Exception as e:
            print "Error decoding with strings: %s" % e
            return code
    
    def extract_video_urls_from_decoded(self, decoded_code):
        """从解码后的代码中提取视频URL"""
        video_urls = []
        
        # 视频文件扩展名模式
        video_patterns = [
            r'["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'["\']([^"\']*\.ts[^"\']*)["\']',
            r'["\']([^"\']*\.mp4[^"\']*)["\']',
            r'["\']([^"\']*\.flv[^"\']*)["\']',
            r'["\']([^"\']*\.avi[^"\']*)["\']',
            r'["\']([^"\']*\.mov[^"\']*)["\']',
            r'["\']([^"\']*http[^"\']*video[^"\']*)["\']',
            r'["\']([^"\']*http[^"\']*stream[^"\']*)["\']'
        ]
        
        for pattern in video_patterns:
            matches = re.findall(pattern, decoded_code, re.IGNORECASE)
            for match in matches:
                if match not in [url['url'] for url in video_urls]:
                    video_urls.append({
                        'url': match,
                        'type': match.split('.')[-1].lower() if '.' in match else 'unknown',
                        'source': 'decoded_packer'
                    })
        
        return video_urls
    
    def decode_file(self, file_path):
        """解码文件中的JavaScript packer"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            return self.decode_packer(content)
            
        except Exception as e:
            print "Error reading file: %s" % e
            return None
    
    def analyze_evil_js(self):
        """分析evil.js文件"""
        print "=== 分析evil.js文件 ==="
        
        try:
            with open('evil.js', 'r') as f:
                content = f.read()
            
            print "文件大小: %d 字符" % len(content)
            
            # 查找eval函数
            eval_pattern = r'eval\s*\([^)]+\)'
            eval_matches = re.findall(eval_pattern, content, re.IGNORECASE)
            print "找到 %d 个eval函数" % len(eval_matches)
            
            # 查找packer模式
            packer_pattern = r'eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*d\s*\)'
            packer_matches = re.findall(packer_pattern, content, re.IGNORECASE)
            print "找到 %d 个packer模式" % len(packer_matches)
            
            # 尝试解码
            decoded = self.decode_packer(content)
            if decoded:
                print "解码成功！"
                print "字符串数组长度: %d" % len(decoded['strings'])
                print "数字数组长度: %d" % len(decoded['numbers'])
                print "基数: %d" % decoded['base']
                
                # 提取视频URL
                video_urls = self.extract_video_urls_from_decoded(decoded['decoded_code'])
                print "找到 %d 个视频URL" % len(video_urls)
                
                for i, url_info in enumerate(video_urls, 1):
                    print "  %d. %s (%s)" % (i, url_info['url'], url_info['type'])
                
                return decoded
            else:
                print "解码失败"
                return None
                
        except Exception as e:
            print "分析失败: %s" % e
            return None

def main():
    """主函数"""
    decoder = JavaScriptPackerDecoder()
    result = decoder.analyze_evil_js()
    
    if result:
        print "\n=== 解码结果 ==="
        print "解码后的代码片段:"
        print result['decoded_code'][:500] + "..."

if __name__ == '__main__':
    main() 