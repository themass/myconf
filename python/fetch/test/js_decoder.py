#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JavaScript解码器
专门用于解密JavaScript代码
支持JavaScript packer解码
支持Base64和URL解码
在解码后的内容中查找视频URL
"""

import re
import base64
import urllib2
from bs4 import BeautifulSoup

class JavaScriptDecoder(object):
    def __init__(self, html_content=None, html_file=None):
        """
        初始化JavaScript解码器
        
        Args:
            html_content: HTML字符串内容
            html_file: HTML文件路径
        """
        self.html_content = html_content
        self.html_file = html_file
        self.soup = None
        self.decoded_scripts = []
        self.video_urls = []
        
        self._load_html()
    
    def _load_html(self):
        """加载HTML内容"""
        if self.html_content:
            self.soup = BeautifulSoup(self.html_content, 'html.parser')
        elif self.html_file:
            try:
                with open(self.html_file, 'r') as f:
                    self.html_content = f.read()
                self.soup = BeautifulSoup(self.html_content, 'html.parser')
            except Exception as e:
                print "Error loading HTML file: %s" % e
        else:
            print "No HTML content or file provided"
    
    def extract_scripts(self):
        """提取所有script标签"""
        scripts = []
        
        if not self.soup:
            return scripts
        
        # 查找所有script标签
        script_tags = self.soup.find_all('script')
        
        for script in script_tags:
            script_content = script.get_text()
            if script_content.strip():
                scripts.append({
                    'content': script_content,
                    'src': script.get('src'),
                    'type': script.get('type', 'text/javascript')
                })
        
        return scripts
    
    def decode_js_packer(self, js_code):
        """
        解码JavaScript Packer
        处理eval(function(p,a,c,k,e,d){...})格式的代码
        """
        decoded_code = js_code
        
        # 查找JavaScript Packer模式
        packer_pattern = r'eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*d\s*\)\s*\{[^}]*\}\s*\([^)]*\)\s*\)'
        
        matches = re.findall(packer_pattern, js_code, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            try:
                # 尝试提取packer函数的参数
                param_pattern = r'\(\s*([^)]+)\s*\)'
                param_match = re.search(param_pattern, match)
                
                if param_match:
                    params = param_match.group(1)
                    # 尝试解码packer参数
                    decoded_params = self.decode_packer_params(params)
                    if decoded_params:
                        decoded_code = decoded_code.replace(match, decoded_params)
                    else:
                        decoded_code = decoded_code.replace(match, '/* DECODED PACKER */')
                    
            except Exception as e:
                print "Error decoding JS packer: %s" % e
        
        return decoded_code
    
    def decode_packer_params(self, params_str):
        """解码packer参数"""
        try:
            # 移除引号并分割参数
            params = params_str.strip("'\"")
            parts = params.split("','")
            
            if len(parts) >= 4:
                # 提取字符串数组
                strings_part = parts[0].strip("'")
                # 提取数字参数
                numbers_part = parts[1].strip("'")
                
                # 尝试解码字符串数组
                strings = self.decode_string_array(strings_part)
                if strings:
                    return strings
                    
        except Exception as e:
            print "Error decoding packer params: %s" % e
        
        return None
    
    def decode_string_array(self, array_str):
        """解码字符串数组"""
        try:
            # 查找字符串数组模式
            array_pattern = r'\[([^\]]+)\]'
            match = re.search(array_pattern, array_str)
            
            if match:
                array_content = match.group(1)
                # 分割字符串
                strings = [s.strip('"\'') for s in array_content.split(',')]
                return ' '.join(strings)
                
        except Exception as e:
            print "Error decoding string array: %s" % e
        
        return None
    
    def decode_base64(self, text):
        """解码Base64编码的内容"""
        decoded_items = []
        
        # 查找Base64编码的字符串
        base64_pattern = r'["\']([A-Za-z0-9+/]{20,}={0,2})["\']'
        matches = re.findall(base64_pattern, text)
        
        for match in matches:
            try:
                decoded = base64.b64decode(match)
                decoded_items.append({
                    'original': match,
                    'decoded': decoded,
                    'type': 'base64'
                })
            except Exception as e:
                # 可能不是有效的Base64
                pass
        
        return decoded_items
    
    def decode_url_encoding(self, text):
        """解码URL编码的内容"""
        decoded_items = []
        
        # 查找URL编码的字符串
        url_pattern = r'["\']([%A-Za-z0-9]{20,})["\']'
        matches = re.findall(url_pattern, text)
        
        for match in matches:
            try:
                decoded = urllib2.unquote(match)
                if decoded != match:
                    decoded_items.append({
                        'original': match,
                        'decoded': decoded,
                        'type': 'url_encoded'
                    })
            except Exception as e:
                pass
        
        return decoded_items
    
    def decode_hex_encoding(self, text):
        """解码十六进制编码的内容"""
        decoded_items = []
        
        # 查找十六进制编码的字符串
        hex_pattern = r'["\']([0-9a-fA-F]{20,})["\']'
        matches = re.findall(hex_pattern, text)
        
        for match in matches:
            try:
                if len(match) % 2 == 0:  # 确保长度是偶数
                    decoded = match.decode('hex')
                    decoded_items.append({
                        'original': match,
                        'decoded': decoded,
                        'type': 'hex'
                    })
            except Exception as e:
                pass
        
        return decoded_items
    
    def decode_rot13(self, text):
        """解码ROT13编码的内容"""
        decoded_items = []
        
        # ROT13解码函数
        def rot13_decode(s):
            result = ""
            for char in s:
                if char.isalpha():
                    ascii_offset = 65 if char.isupper() else 97
                    result += chr((ord(char) - ascii_offset + 13) % 26 + ascii_offset)
                else:
                    result += char
            return result
        
        # 查找可能的ROT13编码字符串
        rot13_pattern = r'["\']([A-Za-z]{10,})["\']'
        matches = re.findall(rot13_pattern, text)
        
        for match in matches:
            decoded = rot13_decode(match)
            if decoded != match:
                decoded_items.append({
                    'original': match,
                    'decoded': decoded,
                    'type': 'rot13'
                })
        
        return decoded_items
    
    def find_video_urls_in_decoded(self, decoded_content):
        """在解码后的内容中查找视频URL"""
        video_urls = []
        
        # 视频文件扩展名模式
        video_patterns = [
            r'["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'["\']([^"\']*\.ts[^"\']*)["\']',
            r'["\']([^"\']*\.mp4[^"\']*)["\']',
            r'["\']([^"\']*\.flv[^"\']*)["\']',
            r'["\']([^"\']*\.avi[^"\']*)["\']',
            r'["\']([^"\']*\.mov[^"\']*)["\']'
        ]
        
        for pattern in video_patterns:
            matches = re.findall(pattern, decoded_content, re.IGNORECASE)
            for match in matches:
                if match not in [url['url'] for url in video_urls]:
                    video_urls.append({
                        'url': match,
                        'type': match.split('.')[-1].lower(),
                        'source': 'decoded_js'
                    })
        
        return video_urls
    
    def decode_all_scripts(self):
        """解码所有JavaScript脚本"""
        scripts = self.extract_scripts()
        
        for script in scripts:
            script_content = script['content']
            decoded_script = {
                'original': script_content,
                'src': script['src'],
                'type': script['type'],
                'decoded_content': script_content,
                'base64_decoded': [],
                'url_decoded': [],
                'hex_decoded': [],
                'rot13_decoded': [],
                'video_urls': []
            }
            
            # 解码JavaScript Packer
            decoded_script['decoded_content'] = self.decode_js_packer(script_content)
            
            # 解码Base64
            decoded_script['base64_decoded'] = self.decode_base64(script_content)
            
            # 解码URL编码
            decoded_script['url_decoded'] = self.decode_url_encoding(script_content)
            
            # 解码十六进制
            decoded_script['hex_decoded'] = self.decode_hex_encoding(script_content)
            
            # 解码ROT13
            decoded_script['rot13_decoded'] = self.decode_rot13(script_content)
            
            # 在解码后的内容中查找视频URL
            decoded_script['video_urls'] = self.find_video_urls_in_decoded(decoded_script['decoded_content'])
            
            # 在所有解码结果中查找视频URL
            for decoded_item in (decoded_script['base64_decoded'] + 
                               decoded_script['url_decoded'] + 
                               decoded_script['hex_decoded'] + 
                               decoded_script['rot13_decoded']):
                urls = self.find_video_urls_in_decoded(decoded_item['decoded'])
                for url in urls:
                    if url['url'] not in [u['url'] for u in decoded_script['video_urls']]:
                        decoded_script['video_urls'].append(url)
            
            self.decoded_scripts.append(decoded_script)
            
            # 收集所有视频URL
            for url in decoded_script['video_urls']:
                if url['url'] not in [u['url'] for u in self.video_urls]:
                    self.video_urls.append(url)
        
        return self.decoded_scripts
    
    def parse(self):
        """执行完整的解码流程"""
        self.decode_all_scripts()
        
        results = {
            'decoded_scripts': self.decoded_scripts,
            'video_urls': self.video_urls,
            'total_scripts': len(self.decoded_scripts),
            'total_video_urls': len(self.video_urls)
        }
        
        return results
    
    def print_results(self):
        """打印解码结果"""
        print "=== JavaScript解码结果 ==="
        print "总脚本数量: %d" % len(self.decoded_scripts)
        print "总视频URL数量: %d" % len(self.video_urls)
        
        print "\n解码的脚本:"
        for i, script in enumerate(self.decoded_scripts, 1):
            print "\n脚本 %d:" % i
            if script['src']:
                print "  源文件: %s" % script['src']
            print "  类型: %s" % script['type']
            print "  Base64解码项: %d" % len(script['base64_decoded'])
            print "  URL解码项: %d" % len(script['url_decoded'])
            print "  十六进制解码项: %d" % len(script['hex_decoded'])
            print "  ROT13解码项: %d" % len(script['rot13_decoded'])
            print "  视频URL数量: %d" % len(script['video_urls'])
            
            if script['video_urls']:
                print "  视频URL:"
                for j, url in enumerate(script['video_urls'], 1):
                    print "    %d. %s (%s)" % (j, url['url'], url['type'])
        
        print "\n所有发现的视频URL:"
        for i, url in enumerate(self.video_urls, 1):
            print "  %d. %s (%s) - %s" % (i, url['url'], url['type'], url['source'])

def main():
    """主函数"""
    decoder = JavaScriptDecoder(html_file='index.html')
    results = decoder.parse()
    decoder.print_results()

if __name__ == '__main__':
    main() 