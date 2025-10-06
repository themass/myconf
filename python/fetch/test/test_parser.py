#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本
用于验证各个解析器的功能
"""

import os
import sys
import json
from video_parser import VideoParser
from advanced_video_parser import AdvancedVideoParser
from js_decoder import JavaScriptDecoder
from comprehensive_parser import ComprehensiveParser

def test_basic_parser():
    """测试基础解析器"""
    print "=== 测试基础解析器 ==="
    
    if not os.path.exists('index.html'):
        print "错误: 未找到index.html文件"
        return False
    
    try:
        parser = VideoParser(html_file='index.html')
        results = parser.parse()
        
        print "✓ 基础解析器运行成功"
        print "  标题: %s" % results.get('title', 'N/A')
        print "  视频URL数量: %d" % len(results.get('video_urls', []))
        print "  M3U8 API: %s" % (results.get('m3u8_api', 'N/A'))
        
        return True
    except Exception as e:
        print "✗ 基础解析器测试失败: %s" % e
        return False

def test_advanced_parser():
    """测试高级解析器"""
    print "\n=== 测试高级解析器 ==="
    
    if not os.path.exists('index.html'):
        print "错误: 未找到index.html文件"
        return False
    
    try:
        parser = AdvancedVideoParser(html_file='index.html')
        results = parser.parse()
        
        print "✓ 高级解析器运行成功"
        print "  JavaScript变量数量: %d" % len(results.get('js_variables', {}))
        print "  视频配置数量: %d" % len(results.get('video_configs', []))
        print "  隐藏URL数量: %d" % len(results.get('hidden_urls', []))
        
        return True
    except Exception as e:
        print "✗ 高级解析器测试失败: %s" % e
        return False

def test_js_decoder():
    """测试JavaScript解码器"""
    print "\n=== 测试JavaScript解码器 ==="
    
    if not os.path.exists('index.html'):
        print "错误: 未找到index.html文件"
        return False
    
    try:
        decoder = JavaScriptDecoder(html_file='index.html')
        results = decoder.parse()
        
        print "✓ JavaScript解码器运行成功"
        print "  解码脚本数量: %d" % results.get('total_scripts', 0)
        print "  解码发现视频URL: %d" % results.get('total_video_urls', 0)
        
        return True
    except Exception as e:
        print "✗ JavaScript解码器测试失败: %s" % e
        return False

def test_comprehensive_parser():
    """测试综合解析器"""
    print "\n=== 测试综合解析器 ==="
    
    if not os.path.exists('index.html'):
        print "错误: 未找到index.html文件"
        return False
    
    try:
        parser = ComprehensiveParser(html_file='index.html')
        results = parser.parse()
        
        print "✓ 综合解析器运行成功"
        print "  总视频URL数量: %d" % results['summary'].get('total_video_urls', 0)
        print "  唯一视频URL数量: %d" % results['summary'].get('unique_video_urls', 0)
        print "  视频类型: %s" % ', '.join(results['summary'].get('video_types', []))
        
        # 测试导出功能
        parser.export_results('test_results.json')
        if os.path.exists('test_results.json'):
            print "✓ 结果导出功能正常"
            os.remove('test_results.json')  # 清理测试文件
        else:
            print "✗ 结果导出功能异常"
        
        return True
    except Exception as e:
        print "✗ 综合解析器测试失败: %s" % e
        return False

def test_dependencies():
    """测试依赖包"""
    print "=== 测试依赖包 ==="
    
    dependencies = [
        'bs4',
        'urllib2',
        'json',
        're',
        'base64'
    ]
    
    all_passed = True
    
    for dep in dependencies:
        try:
            __import__(dep)
            print "✓ %s 导入成功" % dep
        except ImportError as e:
            print "✗ %s 导入失败: %s" % (dep, e)
            all_passed = False
    
    return all_passed

def create_test_html():
    """创建测试用的HTML文件"""
    test_html = """
<!DOCTYPE html>
<html>
<head>
    <title>测试视频页面</title>
    <meta property="og:title" content="测试视频标题">
    <meta property="og:description" content="这是一个测试视频描述">
    <meta property="og:image" content="http://example.com/thumbnail.jpg">
</head>
<body>
    <h1>测试视频</h1>
    <div id="video-container">
        <video src="http://example.com/video.mp4" controls></video>
    </div>
    
    <script>
        var video_id = "test123";
        var video_url = "http://example.com/video.m3u8";
        var config = {
            "player": "html5",
            "quality": "hd"
        };
        
        // Base64编码的URL
        var encoded_url = "aHR0cDovL2V4YW1wbGUuY29tL3ZpZGVvMi5tcDQ=";
        
        // URL编码的URL
        var url_encoded = "http%3A//example.com/video3.mp4";
    </script>
</body>
</html>
"""
    
    with open('test.html', 'w') as f:
        f.write(test_html)
    
    print "✓ 测试HTML文件已创建: test.html"

def run_all_tests():
    """运行所有测试"""
    print "开始运行所有测试..."
    print "=" * 50
    
    # 测试依赖
    deps_ok = test_dependencies()
    
    # 创建测试HTML文件
    create_test_html()
    
    # 测试各个解析器
    tests = [
        test_basic_parser,
        test_advanced_parser,
        test_js_decoder,
        test_comprehensive_parser
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print "\n" + "=" * 50
    print "测试结果汇总:"
    print "依赖包测试: %s" % ("通过" if deps_ok else "失败")
    print "解析器测试: %d/%d 通过" % (passed, total)
    
    if deps_ok and passed == total:
        print "✓ 所有测试通过！"
        return True
    else:
        print "✗ 部分测试失败"
        return False

def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--basic':
            test_basic_parser()
        elif sys.argv[1] == '--advanced':
            test_advanced_parser()
        elif sys.argv[1] == '--js':
            test_js_decoder()
        elif sys.argv[1] == '--comprehensive':
            test_comprehensive_parser()
        elif sys.argv[1] == '--deps':
            test_dependencies()
        else:
            print "用法: python test_parser.py [--basic|--advanced|--js|--comprehensive|--deps]"
    else:
        run_all_tests()

if __name__ == '__main__':
    main() 