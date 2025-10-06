#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单JavaScript分析器
直接分析evil.js文件结构并提取视频URL
"""

import re
import base64

class SimpleJavaScriptAnalyzer(object):
    def __init__(self):
        self.results = []
    
    def analyze_evil_js_simple(self):
        """简单分析evil.js文件"""
        print "=== 简单分析evil.js文件 ==="
        
        try:
            with open('evil.js', 'r') as f:
                content = f.read()
            
            print "文件大小: %d 字符" % len(content)
            
            # 1. 查找所有可能的URL
            self.find_urls(content)
            
            # 2. 查找Base64编码的内容
            self.find_base64_content(content)
            
            # 3. 查找视频相关的字符串
            self.find_video_strings(content)
            
            # 4. 查找加密的字符串数组
            self.find_encrypted_arrays(content)
            
            # 5. 尝试简单的解码
            self.try_simple_decoding(content)
            
            return self.results
            
        except Exception as e:
            print "分析失败: %s" % e
            return []
    
    def find_urls(self, content):
        """查找所有可能的URL"""
        print "\n=== 查找URL ==="
        
        # URL模式
        url_patterns = [
            r'https?://[^\s"\'<>]+',
            r'["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'["\']([^"\']*\.ts[^"\']*)["\']',
            r'["\']([^"\']*\.mp4[^"\']*)["\']',
            r'["\']([^"\']*video[^"\']*)["\']',
            r'["\']([^"\']*stream[^"\']*)["\']',
            r'["\']([^"\']*play[^"\']*)["\']'
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if match and len(match) > 10:
                    print "找到URL: %s" % match
                    self.results.append({
                        'type': 'url',
                        'value': match,
                        'source': 'direct_search'
                    })
    
    def find_base64_content(self, content):
        """查找Base64编码的内容"""
        print "\n=== 查找Base64内容 ==="
        
        # Base64模式
        base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
        matches = re.findall(base64_pattern, content)
        
        for match in matches:
            if len(match) > 20:  # 只处理较长的Base64字符串
                try:
                    decoded = base64.b64decode(match)
                    if self.is_printable(decoded):
                        print "Base64解码: %s -> %s" % (match[:50], decoded[:100])
                        self.results.append({
                            'type': 'base64',
                            'encoded': match,
                            'decoded': decoded,
                            'source': 'base64_decode'
                        })
                except:
                    pass
    
    def find_video_strings(self, content):
        """查找视频相关的字符串"""
        print "\n=== 查找视频字符串 ==="
        
        # 视频相关关键词
        video_keywords = [
            'video', 'stream', 'play', 'media', 'm3u8', 'ts', 'mp4', 'flv',
            'player', 'source', 'src', 'url', 'link', 'file'
        ]
        
        for keyword in video_keywords:
            pattern = r'["\']([^"\']*' + keyword + r'[^"\']*)["\']'
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match) > 5:
                    print "视频相关: %s" % match
                    self.results.append({
                        'type': 'video_string',
                        'value': match,
                        'keyword': keyword,
                        'source': 'keyword_search'
                    })
    
    def find_encrypted_arrays(self, content):
        """查找加密的字符串数组"""
        print "\n=== 查找加密数组 ==="
        
        # 查找长字符串数组
        array_pattern = r'\[([^\]]{100,})\]'
        matches = re.findall(array_pattern, content)
        
        for i, match in enumerate(matches):
            print "加密数组 %d: %s..." % (i+1, match[:100])
            
            # 尝试分割数组
            parts = match.split(',')
            if len(parts) > 10:
                print "  数组长度: %d" % len(parts)
                print "  前5个元素: %s" % parts[:5]
                
                self.results.append({
                    'type': 'encrypted_array',
                    'index': i+1,
                    'length': len(parts),
                    'sample': parts[:5],
                    'source': 'array_analysis'
                })
    
    def try_simple_decoding(self, content):
        """尝试简单解码"""
        print "\n=== 尝试简单解码 ==="
        
        # 查找可能的编码字符串
        encoded_patterns = [
            r'["\']([A-Za-z0-9+/]{20,})["\']',  # Base64
            r'["\']([A-Fa-f0-9]{20,})["\']',     # Hex
            r'["\']([A-Za-z0-9%]{20,})["\']'     # URL编码
        ]
        
        for pattern in encoded_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) > 20:
                    # 尝试URL解码
                    try:
                        import urllib
                        url_decoded = urllib.unquote(match)
                        if url_decoded != match:
                            print "URL解码: %s -> %s" % (match[:50], url_decoded[:100])
                            self.results.append({
                                'type': 'url_decoded',
                                'original': match,
                                'decoded': url_decoded,
                                'source': 'url_decode'
                            })
                    except:
                        pass
    
    def is_printable(self, text):
        """检查字符串是否可打印"""
        try:
            return all(32 <= ord(c) <= 126 for c in text)
        except:
            return False
    
    def extract_video_urls(self):
        """提取视频URL"""
        video_urls = []
        
        for result in self.results:
            if result['type'] == 'url':
                url = result['value']
                if any(ext in url.lower() for ext in ['.m3u8', '.ts', '.mp4', '.flv', 'video', 'stream']):
                    video_urls.append(url)
            elif result['type'] == 'base64':
                decoded = result['decoded']
                if any(ext in decoded.lower() for ext in ['.m3u8', '.ts', '.mp4', '.flv', 'video', 'stream']):
                    video_urls.append(decoded)
            elif result['type'] == 'url_decoded':
                decoded = result['decoded']
                if any(ext in decoded.lower() for ext in ['.m3u8', '.ts', '.mp4', '.flv', 'video', 'stream']):
                    video_urls.append(decoded)
        
        return video_urls
    
    def print_summary(self):
        """打印分析摘要"""
        print "\n=== 分析摘要 ==="
        print "总结果数量: %d" % len(self.results)
        
        # 按类型统计
        type_counts = {}
        for result in self.results:
            result_type = result['type']
            type_counts[result_type] = type_counts.get(result_type, 0) + 1
        
        for result_type, count in type_counts.items():
            print "%s: %d" % (result_type, count)
        
        # 提取视频URL
        video_urls = self.extract_video_urls()
        print "找到视频URL: %d" % len(video_urls)
        
        for i, url in enumerate(video_urls, 1):
            print "  %d. %s" % (i, url)

def main():
    """主函数"""
    analyzer = SimpleJavaScriptAnalyzer()
    results = analyzer.analyze_evil_js_simple()
    analyzer.print_summary()

if __name__ == '__main__':
    main() 