#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基础视频解析器
提取HTML中的基本信息（标题、描述、缩略图等）
查找m3u8 API链接
尝试获取视频播放列表
"""

import re
import json
import urllib2
from bs4 import BeautifulSoup
from urlparse import urljoin, urlparse

class VideoParser(object):
    def __init__(self, html_content=None, html_file=None):
        """
        初始化视频解析器
        
        Args:
            html_content: HTML字符串内容
            html_file: HTML文件路径
        """
        self.html_content = html_content
        self.html_file = html_file
        self.soup = None
        self.results = {
            'title': None,
            'video_id': None,
            'm3u8_api': None,
            'thumbnail': None,
            'description': None,
            'duration': None,
            'upload_date': None,
            'interaction_count': None,
            'video_urls': [],
            'sources': []
        }
        
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
    
    def extract_basic_info(self):
        """提取基本信息"""
        if not self.soup:
            return self.results
        
        # 提取标题
        title_selectors = [
            'title',
            'meta[property="og:title"]',
            'meta[name="title"]',
            'h1',
            '.title',
            '#title'
        ]
        
        for selector in title_selectors:
            element = self.soup.select_one(selector)
            if element:
                if selector == 'title':
                    self.results['title'] = element.get_text().strip()
                else:
                    self.results['title'] = element.get('content', element.get_text()).strip()
                break
        
        # 提取描述
        desc_selectors = [
            'meta[property="og:description"]',
            'meta[name="description"]',
            '.description',
            '#description'
        ]
        
        for selector in desc_selectors:
            element = self.soup.select_one(selector)
            if element:
                self.results['description'] = element.get('content', element.get_text()).strip()
                break
        
        # 提取缩略图
        thumbnail_selectors = [
            'meta[property="og:image"]',
            'meta[name="thumbnail"]',
            '.thumbnail img',
            '#thumbnail img'
        ]
        
        for selector in thumbnail_selectors:
            element = self.soup.select_one(selector)
            if element:
                self.results['thumbnail'] = element.get('content', element.get('src'))
                break
        
        # 提取视频ID
        video_id_patterns = [
            r'video_id["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',
            r'id["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',
            r'data-video-id["\']?\s*[:=]\s*["\']?([^"\']+)["\']?'
        ]
        
        for pattern in video_id_patterns:
            match = re.search(pattern, self.html_content)
            if match:
                self.results['video_id'] = match.group(1)
                break
        
        return self.results
    
    def find_m3u8_api(self):
        """查找m3u8 API链接"""
        if not self.soup:
            return self.results
        
        # 忽略特定的m3u8 API，专注于从加密JS中提取视频
        # 查找m3u8相关的API链接（排除已知的无效API）
        m3u8_patterns = [
            r'["\']([^"\']*m3u8[^"\']*)["\']',
            r'["\']([^"\']*playlist[^"\']*)["\']',
            r'["\']([^"\']*api[^"\']*video[^"\']*)["\']',
            r'["\']([^"\']*stream[^"\']*)["\']'
        ]
        
        for pattern in m3u8_patterns:
            matches = re.findall(pattern, self.html_content, re.IGNORECASE)
            for match in matches:
                # 忽略已知的无效API
                if 'gimy.life/search/m3u8' in match:
                    continue
                    
                if 'm3u8' in match.lower() or 'playlist' in match.lower():
                    self.results['m3u8_api'] = match
                    self.results['sources'].append({
                        'url': match,
                        'type': 'm3u8_api',
                        'source': 'html_direct'
                    })
                    break
        
        return self.results
    
    def extract_video_urls(self):
        """提取视频URL"""
        if not self.soup:
            return self.results
        
        # 查找视频文件URL
        video_patterns = [
            r'["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'["\']([^"\']*\.ts[^"\']*)["\']',
            r'["\']([^"\']*\.mp4[^"\']*)["\']',
            r'["\']([^"\']*\.flv[^"\']*)["\']'
        ]
        
        for pattern in video_patterns:
            matches = re.findall(pattern, self.html_content, re.IGNORECASE)
            for match in matches:
                if match not in [url['url'] for url in self.results['video_urls']]:
                    self.results['video_urls'].append({
                        'url': match,
                        'type': match.split('.')[-1].lower(),
                        'source': 'html_direct'
                    })
        
        return self.results
    
    def get_m3u8_playlist(self, api_url=None):
        """获取m3u8播放列表"""
        if not api_url:
            api_url = self.results.get('m3u8_api')
        
        if not api_url:
            return None
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://example.com/',
                'Accept': '*/*'
            }
            
            req = urllib2.Request(api_url, headers=headers)
            response = urllib2.urlopen(req)
            playlist_content = response.read()
            
            # 解析m3u8播放列表
            ts_urls = []
            for line in playlist_content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and (line.endswith('.ts') or line.endswith('.m3u8')):
                    if not line.startswith('http'):
                        line = urljoin(api_url, line)
                    ts_urls.append(line)
            
            return {
                'playlist_url': api_url,
                'ts_urls': ts_urls,
                'content': playlist_content
            }
            
        except Exception as e:
            print "Error fetching m3u8 playlist: %s" % e
            return None
    
    def parse(self):
        """执行完整的解析流程"""
        self.extract_basic_info()
        self.find_m3u8_api()
        self.extract_video_urls()
        
        # 尝试获取m3u8播放列表
        if self.results.get('m3u8_api'):
            playlist = self.get_m3u8_playlist()
            if playlist:
                self.results['m3u8_playlist'] = playlist
        
        return self.results
    
    def print_results(self):
        """打印解析结果"""
        print "=== 视频解析结果 ==="
        title = self.results.get('title', 'N/A')
        if isinstance(title, unicode):
            title = title.encode('utf-8', 'ignore')
        print "标题: %s" % title
        
        video_id = self.results.get('video_id', 'N/A')
        if isinstance(video_id, unicode):
            video_id = video_id.encode('utf-8', 'ignore')
        print "视频ID: %s" % video_id
        
        description = self.results.get('description', 'N/A')
        if isinstance(description, unicode):
            description = description.encode('utf-8', 'ignore')
        print "描述: %s" % description
        
        thumbnail = self.results.get('thumbnail', 'N/A')
        if isinstance(thumbnail, unicode):
            thumbnail = thumbnail.encode('utf-8', 'ignore')
        print "缩略图: %s" % thumbnail
        
        m3u8_api = self.results.get('m3u8_api', 'N/A')
        if isinstance(m3u8_api, unicode):
            m3u8_api = m3u8_api.encode('utf-8', 'ignore')
        print "M3U8 API: %s" % m3u8_api
        
        print "\n视频URL列表:"
        for i, url_info in enumerate(self.results['video_urls'], 1):
            print "  %d. %s (%s) - %s" % (i, url_info['url'], url_info['type'], url_info['source'])
        
        if self.results.get('m3u8_playlist'):
            print "\nM3U8播放列表:"
            print "  播放列表URL: %s" % self.results['m3u8_playlist']['playlist_url']
            print "  TS文件数量: %d" % len(self.results['m3u8_playlist']['ts_urls'])

def main():
    """主函数"""
    # 使用默认的index.html文件
    parser = VideoParser(html_file='index.html')
    results = parser.parse()
    parser.print_results()

if __name__ == '__main__':
    main() 