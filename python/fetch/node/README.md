# JavaScript视频地址解密工具

这是一个专门用于解密JavaScript Packer加密视频地址的Node.js工具。

## 功能特性

- 🔓 解密JavaScript Packer加密代码
- 🎥 自动提取视频URL（m3u8、ts、mp4等格式）
- 📄 支持HTML文件分析
- 🛡️ 安全的代码执行环境
- 📊 详细的解密结果报告

## 安装

```bash
# 克隆项目
git clone <repository-url>
cd video-decoder

# 安装依赖
npm install
```

## 使用方法

### 1. 解密HTML文件

```bash
node index.js index.html
```

### 2. 解密JavaScript代码

```bash
node index.js "eval(function(p,a,c,k,e,d){...})"
```

### 3. 运行测试

```bash
npm test
# 或
node test.js
```

## 项目结构

```
node/
├── index.js          # 主解密脚本
├── test.js           # 测试脚本
├── package.json      # 项目配置
├── README.md         # 说明文档
└── index.html        # 示例HTML文件
```

## API说明

### VideoDecoder类

#### 构造函数
```javascript
const decoder = new VideoDecoder();
```

#### decode(input)
解密输入内容并提取视频URL

**参数:**
- `input` (string): HTML文件路径或JavaScript代码

**返回值:**
```javascript
{
  packerScripts: [],    // 找到的Packer脚本
  videoUrls: [],        // 提取的视频URL
  decodedCode: []       // 解密后的代码
}
```

#### decodePacker(jsCode)
解密JavaScript Packer代码

**参数:**
- `jsCode` (string): 加密的JavaScript代码

**返回值:**
- `string|null`: 解密后的代码或null

#### extractVideoUrls(decodedCode)
从解密后的代码中提取视频URL

**参数:**
- `decodedCode` (string): 解密后的代码

**返回值:**
- `Array`: 视频URL数组

## 支持的视频格式

- `.m3u8` - HLS播放列表
- `.ts` - MPEG传输流
- `.mp4` - MP4视频文件
- `.avi` - AVI视频文件
- `.mov` - QuickTime视频文件
- `.wmv` - Windows Media视频文件
- `.flv` - Flash视频文件
- `.webm` - WebM视频文件

## 安全特性

- 使用Node.js VM模块创建隔离的执行环境
- 模拟浏览器环境（document、window、navigator等）
- 防止恶意代码执行
- 安全的错误处理

## 示例输出

```
开始解密视频地址...

找到 2 个JavaScript Packer代码块

正在解密第 1 个代码块...
找到 3 个视频URL:
  - https://example.com/video1.m3u8
  - https://example.com/video2.ts
  - https://example.com/video3.mp4

正在解密第 2 个代码块...
找到 1 个视频URL:
  - https://example.com/video4.mp4

=== 解密结果 ===
找到 4 个视频URL
解密了 2 个代码块

视频URL列表:
1. https://example.com/video1.m3u8
2. https://example.com/video2.ts
3. https://example.com/video3.mp4
4. https://example.com/video4.mp4

结果已保存到: decoded_results.json
```

## 注意事项

1. 确保输入的JavaScript代码是有效的Packer格式
2. 某些复杂的加密可能需要额外的处理
3. 建议在安全的环境中运行
4. 遵守相关法律法规，仅用于合法用途

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个工具。 