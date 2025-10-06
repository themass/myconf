#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
综合解析器
结合所有功能的完整解析器
提供最全面的视频信息提取
推荐使用这个脚本
"""

import re
import json
import urllib2
from bs4 import BeautifulSoup
from urlparse import urljoin, urlparse
from video_parser import VideoParser
from advanced_video_parser import AdvancedVideoParser
from js_decoder import JavaScriptDecoder

class ComprehensiveParser(object):
    def __init__(self, html_content=None, html_file=None):
        """
        初始化综合解析器
        
        Args:
            html_content: HTML字符串内容
            html_file: HTML文件路径
        """
        self.html_content = html_content
        self.html_file = html_file
        self.soup = None
        
        # 初始化各个解析器
        self.basic_parser = VideoParser(html_content, html_file)
        self.advanced_parser = AdvancedVideoParser(html_content, html_file)
        self.js_decoder = JavaScriptDecoder(html_content, html_file)
        
        # 综合结果
        self.results = {
            'basic_info': {},
            'advanced_info': {},
            'js_decoded_info': {},
            'comprehensive_video_urls': [],
            'all_sources': [],
            'summary': {}
        }
    
    def run_basic_parser(self):
        """运行基础解析器"""
        print "正在运行基础解析器..."
        self.results['basic_info'] = self.basic_parser.parse()
        return self.results['basic_info']
    
    def run_advanced_parser(self):
        """运行高级解析器"""
        print "正在运行高级解析器..."
        self.results['advanced_info'] = self.advanced_parser.parse()
        return self.results['advanced_info']
    
    def run_js_decoder(self):
        """运行JavaScript解码器"""
        print "正在运行JavaScript解码器..."
        self.results['js_decoded_info'] = self.js_decoder.parse()
        return self.results['js_decoded_info']
    
    def analyze_evil_js_file(self):
        """专门分析evil.js文件"""
        print "正在分析evil.js文件..."
        
        try:
            import os
            if os.path.exists('evil.js'):
                with open('evil.js', 'r') as f:
                    evil_content = f.read()
                
                # 查找视频相关的字符串
                video_patterns = [
                    r'["\']([^"\']*\.m3u8[^"\']*)["\']',
                    r'["\']([^"\']*\.ts[^"\']*)["\']',
                    r'["\']([^"\']*\.mp4[^"\']*)["\']',
                    r'["\']([^"\']*video[^"\']*)["\']',
                    r'["\']([^"\']*stream[^"\']*)["\']',
                    r'["\']([^"\']*play[^"\']*)["\']'
                ]
                
                evil_urls = []
                for pattern in video_patterns:
                    matches = re.findall(pattern, evil_content, re.IGNORECASE)
                    for match in matches:
                        if match and len(match) > 10:
                            evil_urls.append({
                                'url': match,
                                'type': match.split('.')[-1].lower() if '.' in match else 'unknown',
                                'source': 'evil_js_file'
                            })
                
                # 查找加密的字符串数组
                array_pattern = r'\[([^\]]{100,})\]'
                array_matches = re.findall(array_pattern, evil_content)
                
                evil_analysis = {
                    'file_size': len(evil_content),
                    'video_urls': evil_urls,
                    'encrypted_arrays': len(array_matches),
                    'has_eval_function': 'eval(' in evil_content,
                    'has_packer_pattern': 'function(p,a,c,k,e,d)' in evil_content
                }
                
                self.results['evil_js_analysis'] = evil_analysis
                print "evil.js分析完成，找到 %d 个视频URL" % len(evil_urls)
                
        except Exception as e:
            print "分析evil.js文件失败: %s" % e
            self.results['evil_js_analysis'] = {'error': str(e)}
    
    def merge_video_urls(self):
        """合并所有来源的视频URL"""
        all_urls = []
        
        # 从基础解析器获取URL
        basic_urls = self.results['basic_info'].get('video_urls', [])
        for url in basic_urls:
            all_urls.append({
                'url': url['url'],
                'type': url['type'],
                'source': 'basic_parser'
            })
        
        # 从高级解析器获取URL
        advanced_urls = self.results['advanced_info'].get('video_urls', [])
        for url in advanced_urls:
            if url['url'] not in [u['url'] for u in all_urls]:
                all_urls.append({
                    'url': url['url'],
                    'type': url['type'],
                    'source': 'advanced_parser'
                })
        
        # 从JavaScript解码器获取URL
        js_urls = self.results['js_decoded_info'].get('video_urls', [])
        for url in js_urls:
            if url['url'] not in [u['url'] for u in all_urls]:
                all_urls.append({
                    'url': url['url'],
                    'type': url['type'],
                    'source': 'js_decoder'
                })
        
        self.results['comprehensive_video_urls'] = all_urls
        return all_urls
    
    def analyze_video_quality(self):
        """分析视频质量信息"""
        quality_info = {
            'hd_urls': [],
            'sd_urls': [],
            'unknown_quality': [],
            'quality_levels': set()
        }
        
        for url_info in self.results['comprehensive_video_urls']:
            url = url_info['url'].lower()
            
            # 根据URL特征判断质量
            if any(keyword in url for keyword in ['1080p', 'hd', 'high', '720p']):
                quality_info['hd_urls'].append(url_info)
                quality_info['quality_levels'].add('HD')
            elif any(keyword in url for keyword in ['480p', 'sd', 'low', '360p']):
                quality_info['sd_urls'].append(url_info)
                quality_info['quality_levels'].add('SD')
            else:
                quality_info['unknown_quality'].append(url_info)
                quality_info['quality_levels'].add('Unknown')
        
        quality_info['quality_levels'] = list(quality_info['quality_levels'])
        return quality_info
    
    def generate_summary(self):
        """生成综合摘要"""
        summary = {
            'total_video_urls': len(self.results['comprehensive_video_urls']),
            'unique_video_urls': len(set(url['url'] for url in self.results['comprehensive_video_urls'])),
            'video_types': list(set(url['type'] for url in self.results['comprehensive_video_urls'])),
            'sources': list(set(url['source'] for url in self.results['comprehensive_video_urls'])),
            'has_m3u8_playlist': bool(self.results['basic_info'].get('m3u8_playlist')),
            'has_js_variables': bool(self.results['advanced_info'].get('js_variables')),
            'has_decoded_scripts': bool(self.results['js_decoded_info'].get('decoded_scripts')),
            'title': self.results['basic_info'].get('title'),
            'video_id': self.results['basic_info'].get('video_id'),
            'thumbnail': self.results['basic_info'].get('thumbnail')
        }
        
        # 添加质量分析
        quality_info = self.analyze_video_quality()
        summary['quality_levels'] = quality_info['quality_levels']
        summary['hd_count'] = len(quality_info['hd_urls'])
        summary['sd_count'] = len(quality_info['sd_urls'])
        
        self.results['summary'] = summary
        return summary
    
    def export_results(self, output_file=None):
        """导出结果到文件"""
        if not output_file:
            output_file = 'video_parse_results.json'
        
        # 准备导出数据
        export_data = {
            'summary': self.results['summary'],
            'video_urls': self.results['comprehensive_video_urls'],
            'basic_info': self.results['basic_info'],
            'advanced_info': {
                'js_variables': self.results['advanced_info'].get('js_variables', {}),
                'video_configs': self.results['advanced_info'].get('video_configs', []),
                'video_structure': self.results['advanced_info'].get('video_structure', {}),
                'hidden_urls': self.results['advanced_info'].get('hidden_urls', [])
            },
            'js_decoded_info': {
                'total_scripts': self.results['js_decoded_info'].get('total_scripts', 0),
                'total_video_urls': self.results['js_decoded_info'].get('total_video_urls', 0)
            }
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            print "结果已导出到: %s" % output_file
        except Exception as e:
            print "导出失败: %s" % e
    
    def parse(self):
        """执行完整的综合解析流程"""
        print "开始综合视频解析..."
        print "=" * 50
        
        # 运行所有解析器
        self.run_basic_parser()
        self.run_advanced_parser()
        self.run_js_decoder()
        
        # 专门分析evil.js文件
        self.analyze_evil_js_file()
        
        # 合并结果
        self.merge_video_urls()
        
        # 生成摘要
        self.generate_summary()
        
        print "=" * 50
        print "综合解析完成!"
        
        return self.results
    
    def print_comprehensive_results(self):
        """打印综合解析结果"""
        print "\n" + "=" * 60
        print "综合视频解析结果"
        print "=" * 60
        
        # 打印摘要
        summary = self.results['summary']
        print "\n=== 解析摘要 ==="
        title = summary.get('title', 'N/A')
        if isinstance(title, unicode):
            title = title.encode('utf-8', 'ignore')
        print "标题: %s" % title
        
        video_id = summary.get('video_id', 'N/A')
        if isinstance(video_id, unicode):
            video_id = video_id.encode('utf-8', 'ignore')
        print "视频ID: %s" % video_id
        
        thumbnail = summary.get('thumbnail', 'N/A')
        if isinstance(thumbnail, unicode):
            thumbnail = thumbnail.encode('utf-8', 'ignore')
        print "缩略图: %s" % thumbnail
        
        print "总视频URL数量: %d" % summary.get('total_video_urls', 0)
        print "唯一视频URL数量: %d" % summary.get('unique_video_urls', 0)
        print "视频类型: %s" % ', '.join(summary.get('video_types', []))
        print "质量等级: %s" % ', '.join(summary.get('quality_levels', []))
        print "HD视频数量: %d" % summary.get('hd_count', 0)
        print "SD视频数量: %d" % summary.get('sd_count', 0)
        
        # 打印视频URL
        print "\n=== 所有视频URL ==="
        for i, url_info in enumerate(self.results['comprehensive_video_urls'], 1):
            print "%d. %s (%s) - %s" % (i, url_info['url'], url_info['type'], url_info['source'])
        
        # 打印M3U8播放列表信息
        if self.results['basic_info'].get('m3u8_playlist'):
            playlist = self.results['basic_info']['m3u8_playlist']
            print "\n=== M3U8播放列表 ==="
            print "播放列表URL: %s" % playlist['playlist_url']
            print "TS文件数量: %d" % len(playlist['ts_urls'])
        
        # 打印JavaScript变量
        js_vars = self.results['advanced_info'].get('js_variables', {})
        if js_vars:
            print "\n=== JavaScript变量 ==="
            for var_name, var_value in js_vars.items():
                print "%s = %s" % (var_name, var_value)
        
        # 打印隐藏URL
        hidden_urls = self.results['advanced_info'].get('hidden_urls', [])
        if hidden_urls:
            print "\n=== 隐藏URL ==="
            for i, hidden_url in enumerate(hidden_urls, 1):
                print "%d. %s (%s)" % (i, hidden_url['url'], hidden_url['type'])
        
        # 打印解码脚本信息
        decoded_info = self.results['js_decoded_info']
        if decoded_info.get('decoded_scripts'):
            print "\n=== JavaScript解码信息 ==="
            print "解码脚本数量: %d" % decoded_info.get('total_scripts', 0)
            print "解码发现视频URL: %d" % decoded_info.get('total_video_urls', 0)
    
    def get_best_video_url(self):
        """获取最佳视频URL"""
        urls = self.results['comprehensive_video_urls']
        if not urls:
            return None
        
        # 优先级排序
        priority_order = ['m3u8', 'mp4', 'ts', 'flv', 'avi', 'mov']
        
        for priority_type in priority_order:
            for url_info in urls:
                if url_info['type'] == priority_type:
                    return url_info
        
        # 如果没有找到优先类型，返回第一个
        return urls[0]

def main():
    """主函数"""
    # 创建综合解析器
    parser = ComprehensiveParser(html_file='index.html')
    
    # 执行解析
    results = parser.parse()
    
    # 打印结果
    parser.print_comprehensive_results()
    
    # 获取最佳视频URL
    best_url = parser.get_best_video_url()
    if best_url:
        print "\n=== 推荐视频URL ==="
        print "URL: %s" % best_url['url']
        print "类型: %s" % best_url['type']
        print "来源: %s" % best_url['source']
    
    # 导出结果
    parser.export_results()

if __name__ == '__main__':
    main() 