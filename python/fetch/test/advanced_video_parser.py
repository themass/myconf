#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
高级视频解析器
包含基础解析器的所有功能
提取JavaScript变量
查找潜在的视频URL
分析视频结构
"""

import re
import json
import urllib2
from bs4 import BeautifulSoup
from urlparse import urljoin, urlparse
from video_parser import VideoParser

class AdvancedVideoParser(VideoParser):
    def __init__(self, html_content=None, html_file=None):
        """初始化高级视频解析器"""
        super(AdvancedVideoParser, self).__init__(html_content, html_file)
        self.js_variables = {}
        self.video_configs = []
    
    def extract_js_variables(self):
        """提取JavaScript变量"""
        if not self.html_content:
            return self.js_variables
        
        # 查找JavaScript变量定义
        js_patterns = [
            # var variable = value;
            r'var\s+(\w+)\s*=\s*["\']?([^"\';]+)["\']?;',
            # let variable = value;
            r'let\s+(\w+)\s*=\s*["\']?([^"\';]+)["\']?;',
            # const variable = value;
            r'const\s+(\w+)\s*=\s*["\']?([^"\';]+)["\']?;',
            # variable: value
            r'(\w+)\s*:\s*["\']?([^"\',}]+)["\']?',
            # variable = value
            r'(\w+)\s*=\s*["\']?([^"\';]+)["\']?'
        ]
        
        for pattern in js_patterns:
            matches = re.findall(pattern, self.html_content, re.IGNORECASE)
            for var_name, var_value in matches:
                if var_value.strip() and len(var_value.strip()) > 1:
                    self.js_variables[var_name.strip()] = var_value.strip()
        
        return self.js_variables
    
    def find_video_configs(self):
        """查找视频配置"""
        if not self.html_content:
            return self.video_configs
        
        # 查找视频播放器配置
        config_patterns = [
            r'player\s*\.\s*config\s*=\s*({[^}]+})',
            r'videoConfig\s*=\s*({[^}]+})',
            r'config\s*:\s*({[^}]+})',
            r'options\s*:\s*({[^}]+})',
            r'settings\s*:\s*({[^}]+})'
        ]
        
        for pattern in config_patterns:
            matches = re.findall(pattern, self.html_content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                try:
                    # 尝试解析JSON
                    config = json.loads(match)
                    self.video_configs.append({
                        'config': config,
                        'source': 'js_config'
                    })
                except:
                    # 如果不是有效JSON，保存原始字符串
                    self.video_configs.append({
                        'config': match,
                        'source': 'js_config_raw'
                    })
        
        return self.video_configs
    
    def analyze_video_structure(self):
        """分析视频结构"""
        structure_info = {
            'has_player': False,
            'player_type': None,
            'video_sources': [],
            'quality_levels': [],
            'subtitles': [],
            'chapters': []
        }
        
        if not self.html_content:
            return structure_info
        
        # 检测播放器类型
        player_patterns = {
            'videojs': r'videojs|video\.js',
            'jwplayer': r'jwplayer|jw\.js',
            'flowplayer': r'flowplayer',
            'html5': r'<video[^>]*>',
            'flash': r'swfobject|\.swf',
            'custom': r'player|video-player'
        }
        
        for player_type, pattern in player_patterns.items():
            if re.search(pattern, self.html_content, re.IGNORECASE):
                structure_info['has_player'] = True
                structure_info['player_type'] = player_type
                break
        
        # 查找视频源
        source_patterns = [
            r'<source[^>]*src=["\']([^"\']+)["\'][^>]*>',
            r'src\s*:\s*["\']([^"\']+)["\']',
            r'file\s*:\s*["\']([^"\']+)["\']',
            r'url\s*:\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in source_patterns:
            matches = re.findall(pattern, self.html_content, re.IGNORECASE)
            for match in matches:
                if match not in [s['url'] for s in structure_info['video_sources']]:
                    structure_info['video_sources'].append({
                        'url': match,
                        'type': match.split('.')[-1].lower() if '.' in match else 'unknown'
                    })
        
        # 查找字幕
        subtitle_patterns = [
            r'<track[^>]*src=["\']([^"\']+)["\'][^>]*>',
            r'subtitle\s*:\s*["\']([^"\']+)["\']',
            r'captions\s*:\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in subtitle_patterns:
            matches = re.findall(pattern, self.html_content, re.IGNORECASE)
            for match in matches:
                if match not in structure_info['subtitles']:
                    structure_info['subtitles'].append(match)
        
        return structure_info
    
    def extract_embedded_data(self):
        """提取嵌入数据"""
        embedded_data = []
        
        if not self.html_content:
            return embedded_data
        
        # 查找JSON-LD数据
        json_ld_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
        json_ld_matches = re.findall(json_ld_pattern, self.html_content, re.DOTALL | re.IGNORECASE)
        
        for match in json_ld_matches:
            try:
                data = json.loads(match)
                embedded_data.append({
                    'type': 'json_ld',
                    'data': data
                })
            except:
                pass
        
        # 查找其他JSON数据
        json_pattern = r'<script[^>]*>(.*?var\s+\w+\s*=\s*\{.*?\}.*?)</script>'
        json_matches = re.findall(json_pattern, self.html_content, re.DOTALL | re.IGNORECASE)
        
        for match in json_matches:
            # 尝试提取JSON对象
            json_obj_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_objs = re.findall(json_obj_pattern, match)
            
            for obj in json_objs:
                try:
                    data = json.loads(obj)
                    embedded_data.append({
                        'type': 'embedded_json',
                        'data': data
                    })
                except:
                    pass
        
        return embedded_data
    
    def find_hidden_urls(self):
        """查找隐藏的URL"""
        hidden_urls = []
        
        if not self.html_content:
            return hidden_urls
        
        # 查找Base64编码的URL
        base64_pattern = r'["\']([A-Za-z0-9+/]{20,}={0,2})["\']'
        base64_matches = re.findall(base64_pattern, self.html_content)
        
        for match in base64_matches:
            try:
                import base64
                decoded = base64.b64decode(match)
                if decoded.startswith('http'):
                    hidden_urls.append({
                        'url': decoded,
                        'type': 'base64_decoded',
                        'original': match
                    })
            except:
                pass
        
        # 查找URL编码的URL
        url_encoded_pattern = r'["\']([%A-Za-z0-9]{20,})["\']'
        url_encoded_matches = re.findall(url_encoded_pattern, self.html_content)
        
        for match in url_encoded_matches:
            try:
                decoded = urllib2.unquote(match)
                if decoded.startswith('http') and decoded != match:
                    hidden_urls.append({
                        'url': decoded,
                        'type': 'url_decoded',
                        'original': match
                    })
            except:
                pass
        
        return hidden_urls
    
    def parse(self):
        """执行完整的高级解析流程"""
        # 调用基础解析
        super(AdvancedVideoParser, self).parse()
        
        # 执行高级解析
        self.extract_js_variables()
        self.find_video_configs()
        
        # 添加高级解析结果
        self.results['js_variables'] = self.js_variables
        self.results['video_configs'] = self.video_configs
        self.results['video_structure'] = self.analyze_video_structure()
        self.results['embedded_data'] = self.extract_embedded_data()
        self.results['hidden_urls'] = self.find_hidden_urls()
        
        # 将隐藏URL添加到视频URL列表
        for hidden_url in self.results['hidden_urls']:
            if hidden_url['url'] not in [url['url'] for url in self.results['video_urls']]:
                self.results['video_urls'].append({
                    'url': hidden_url['url'],
                    'type': 'hidden',
                    'source': hidden_url['type']
                })
        
        return self.results
    
    def print_results(self):
        """打印高级解析结果"""
        super(AdvancedVideoParser, self).print_results()
        
        print "\n=== 高级解析结果 ==="
        
        print "\nJavaScript变量:"
        for var_name, var_value in self.js_variables.items():
            print "  %s = %s" % (var_name, var_value)
        
        print "\n视频配置:"
        for i, config in enumerate(self.video_configs, 1):
            print "  配置 %d (%s):" % (i, config['source'])
            if isinstance(config['config'], dict):
                for key, value in config['config'].items():
                    print "    %s: %s" % (key, value)
            else:
                print "    %s" % config['config']
        
        print "\n视频结构分析:"
        structure = self.results.get('video_structure', {})
        print "  播放器类型: %s" % structure.get('player_type', 'N/A')
        print "  视频源数量: %d" % len(structure.get('video_sources', []))
        print "  字幕数量: %d" % len(structure.get('subtitles', []))
        
        print "\n嵌入数据:"
        for i, data in enumerate(self.results.get('embedded_data', []), 1):
            print "  数据 %d (%s):" % (i, data['type'])
            if isinstance(data['data'], dict):
                for key, value in data['data'].items():
                    print "    %s: %s" % (key, value)
        
        print "\n隐藏URL:"
        for i, hidden_url in enumerate(self.results.get('hidden_urls', []), 1):
            print "  %d. %s (%s)" % (i, hidden_url['url'], hidden_url['type'])

def main():
    """主函数"""
    parser = AdvancedVideoParser(html_file='index.html')
    results = parser.parse()
    parser.print_results()

if __name__ == '__main__':
    main() 