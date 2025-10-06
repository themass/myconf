# 视频解析脚本使用说明

这个目录包含了用于解析HTML文件中视频地址的Python2脚本。

## 文件说明

### 1. `video_parser.py` - 基础视频解析器
- 提取HTML中的基本信息（标题、描述、缩略图等）
- 查找m3u8 API链接
- 尝试获取视频播放列表

### 2. `advanced_video_parser.py` - 高级视频解析器
- 包含基础解析器的所有功能
- 提取JavaScript变量
- 查找潜在的视频URL
- 分析视频结构

### 3. `js_decoder.py` - JavaScript解码器
- 专门用于解密JavaScript代码
- 支持JavaScript packer解码
- 支持Base64和URL解码
- 在解码后的内容中查找视频URL

### 4. `comprehensive_parser.py` - 综合解析器
- 结合所有功能的完整解析器
- 提供最全面的视频信息提取
- 推荐使用这个脚本

## 使用方法

### 环境要求
```bash
# 安装必要的依赖
pip install beautifulsoup4
```

### 运行脚本
```bash
# 使用综合解析器（推荐）
python comprehensive_parser.py

# 或者使用其他解析器
python video_parser.py
python advanced_video_parser.py
python js_decoder.py
```

## 解析结果说明

### 基本信息
- `title`: 视频标题
- `video_id`: 视频ID
- `m3u8_api`: m3u8播放列表API地址
- `thumbnail`: 视频缩略图
- `description`: 视频描述
- `duration`: 视频时长
- `upload_date`: 上传日期
- `interaction_count`: 互动次数

### 视频URL类型
- `m3u8`: HLS播放列表文件
- `ts`: 视频片段文件
- `mp4`: MP4视频文件

### 来源说明
- `html_direct`: 直接从HTML提取
- `decoded_js`: 从解码的JavaScript中提取
- `m3u8_api`: 通过m3u8 API获取

## 技术原理

### 1. HTML解析
使用BeautifulSoup库解析HTML结构，提取meta标签和JSON-LD数据。

### 2. JavaScript解码
- **JavaScript Packer**: 解码eval函数中的加密字符串
- **Base64解码**: 解码Base64编码的字符串
- **URL解码**: 解码URL编码的字符串

### 3. 视频地址提取
- 正则表达式匹配视频文件扩展名（.m3u8, .ts, .mp4）
- 查找播放器配置中的视频URL
- 解析m3u8播放列表获取视频片段

### 4. API调用
模拟浏览器请求头，调用m3u8 API获取播放列表数据。

## 注意事项

1. **Python2兼容性**: 所有脚本都使用Python2语法
2. **网络请求**: 需要网络连接来获取m3u8数据
3. **反爬虫**: 某些网站可能有反爬虫机制
4. **法律合规**: 请确保在合法范围内使用这些脚本

## 故障排除

### 常见问题
1. **ImportError**: 确保安装了beautifulsoup4
2. **网络错误**: 检查网络连接和防火墙设置
3. **解码失败**: 某些JavaScript加密可能无法解码
4. **API限制**: 某些API可能有访问频率限制

### 调试建议
1. 检查HTML文件是否存在且格式正确
2. 查看控制台输出的错误信息
3. 尝试不同的解析器脚本
4. 手动检查HTML源码中的视频相关信息

## 扩展功能

可以根据需要扩展脚本功能：
- 添加更多视频格式支持
- 实现视频下载功能
- 添加字幕提取功能
- 支持批量处理多个HTML文件 