#!/bin/bash

# 视频解析脚本快速启动脚本

echo "=== 视频解析脚本快速启动 ==="
echo ""

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "错误: 未找到Python，请先安装Python"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
python -c "
try:
    import bs4
    print '✓ BeautifulSoup4 已安装'
except ImportError:
    print '✗ BeautifulSoup4 未安装，请运行: pip install beautifulsoup4'
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "请先安装依赖: ./install.sh"
    exit 1
fi

# 检查HTML文件
if [ ! -f "index.html" ]; then
    echo "警告: 未找到index.html文件"
    echo "请将需要解析的HTML文件命名为index.html并放在当前目录"
    echo ""
fi

echo ""
echo "请选择要运行的解析器:"
echo "1. 基础解析器 (video_parser.py)"
echo "2. 高级解析器 (advanced_video_parser.py)"
echo "3. JavaScript解码器 (js_decoder.py)"
echo "4. 综合解析器 (comprehensive_parser.py) - 推荐"
echo "5. 使用示例 (example.py)"
echo "6. 运行测试 (test_parser.py)"
echo "7. 退出"
echo ""

read -p "请输入选择 (1-7): " choice

case $choice in
    1)
        echo "运行基础解析器..."
        python video_parser.py
        ;;
    2)
        echo "运行高级解析器..."
        python advanced_video_parser.py
        ;;
    3)
        echo "运行JavaScript解码器..."
        python js_decoder.py
        ;;
    4)
        echo "运行综合解析器..."
        python comprehensive_parser.py
        ;;
    5)
        echo "运行使用示例..."
        python example.py
        ;;
    6)
        echo "运行测试..."
        python test_parser.py
        ;;
    7)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo ""
echo "解析完成！" 