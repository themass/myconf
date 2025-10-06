#!/bin/bash

# 视频解析脚本安装脚本
# 适用于Python2环境

echo "=== 视频解析脚本安装程序 ==="
echo "正在检查Python环境..."

# 检查Python版本
python_version=$(python --version 2>&1)
echo "检测到Python版本: $python_version"

# 检查pip
if ! command -v pip &> /dev/null; then
    echo "错误: 未找到pip，请先安装pip"
    exit 1
fi

echo "正在安装依赖包..."

# 安装依赖
pip install -r requirements.txt

# 检查安装结果
echo "正在验证安装..."

# 测试导入
python -c "
try:
    import bs4
    print '✓ BeautifulSoup4 安装成功'
except ImportError:
    print '✗ BeautifulSoup4 安装失败'

try:
    import requests
    print '✓ Requests 安装成功'
except ImportError:
    print '✗ Requests 安装失败'

try:
    import regex
    print '✓ Regex 安装成功'
except ImportError:
    print '✗ Regex 安装失败'

try:
    import simplejson
    print '✓ SimpleJSON 安装成功'
except ImportError:
    print '✗ SimpleJSON 安装失败'

try:
    import urllib3
    print '✓ Urllib3 安装成功'
except ImportError:
    print '✗ Urllib3 安装失败'

try:
    import chardet
    print '✓ Chardet 安装成功'
except ImportError:
    print '✗ Chardet 安装失败'

try:
    import dateutil
    print '✓ DateUtil 安装成功'
except ImportError:
    print '✗ DateUtil 安装失败'

try:
    import colorlog
    print '✓ ColorLog 安装成功'
except ImportError:
    print '✗ ColorLog 安装失败'

try:
    import tqdm
    print '✓ TQDM 安装成功'
except ImportError:
    print '✗ TQDM 安装失败'
"

echo ""
echo "=== 安装完成 ==="
echo "现在可以运行以下命令来测试脚本:"
echo ""
echo "1. 基础解析器:"
echo "   python video_parser.py"
echo ""
echo "2. 高级解析器:"
echo "   python advanced_video_parser.py"
echo ""
echo "3. JavaScript解码器:"
echo "   python js_decoder.py"
echo ""
echo "4. 综合解析器 (推荐):"
echo "   python comprehensive_parser.py"
echo ""
echo "注意: 确保index.html文件存在于当前目录中" 