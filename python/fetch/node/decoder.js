#!/usr/bin/env node

/**
 * 简化的JavaScript视频地址解密器
 */

const fs = require('fs');
const vm = require('vm');

class SimpleVideoDecoder {
    constructor() {
        this.results = {
            videoUrls: [],
            decodedCode: null,
            errors: []
        };
    }

    /**
     * 从HTML文件中提取JavaScript Packer代码
     */
    extractPackerCode(htmlContent) {
        try {
            // 查找script标签中的eval函数
            const scriptPattern = /<script[^>]*>([\s\S]*?)<\/script>/gi;
            const scripts = [];
            let match;

            while ((match = scriptPattern.exec(htmlContent)) !== null) {
                const scriptContent = match[1];
                if (scriptContent.includes('eval(function(p,a,c,k,e,d)')) {
                    scripts.push(scriptContent.trim());
                }
            }

            return scripts;
        } catch (error) {
            this.results.errors.push(`提取Packer代码失败: ${error.message}`);
            return [];
        }
    }

    /**
     * 尝试解密JavaScript Packer代码
     */
    decodePackerCode(jsCode) {
        try {
            // 创建安全的执行环境
            const context = {
                console: {
                    log: (...args) => {
                        console.log('JS Console:', ...args);
                    }
                },
                document: {
                    createElement: (tag) => {
                        const element = {
                            tagName: tag.toUpperCase(),
                            innerHTML: '',
                            innerText: '',
                            textContent: '',
                            style: {},
                            setAttribute: () => {},
                            getAttribute: () => null,
                            appendChild: () => {},
                            removeChild: () => {},
                            write: (content) => {
                                console.log('document.write:', content);
                            }
                        };
                        return element;
                    },
                    getElementById: () => null,
                    getElementsByTagName: () => [],
                    write: (content) => {
                        console.log('document.write:', content);
                    },
                    writeln: (content) => {
                        console.log('document.writeln:', content);
                    }
                },
                window: {
                    document: null,
                    location: null,
                    navigator: null
                },
                location: {
                    host: 'localhost',
                    href: 'http://localhost',
                    protocol: 'http:',
                    hostname: 'localhost',
                    port: '',
                    pathname: '/',
                    search: '',
                    hash: ''
                },
                navigator: {
                    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    languages: ['zh-CN', 'zh', 'en'],
                    platform: 'Win32',
                    cookieEnabled: true,
                    onLine: true
                },
                videojs: {
                    getPlugin: () => ({}),
                    registerPlugin: () => {},
                    getPluginVersion: () => '1.0.0'
                },
                String: String,
                Array: Array,
                Object: Object,
                Math: Math,
                parseInt: parseInt,
                parseFloat: parseFloat,
                isNaN: isNaN,
                escape: escape,
                unescape: unescape,
                encodeURIComponent: encodeURIComponent,
                decodeURIComponent: decodeURIComponent,
                RegExp: RegExp,
                Date: Date,
                setTimeout: setTimeout,
                setInterval: setInterval,
                clearTimeout: clearTimeout,
                clearInterval: clearInterval
            };

            // 创建VM上下文
            const vmContext = vm.createContext(context);
            
            // 执行解密代码
            const result = vm.runInContext(jsCode, vmContext);
            
            return result;
        } catch (error) {
            this.results.errors.push(`解密失败: ${error.message}`);
            return null;
        }
    }

    /**
     * 从解密后的代码中提取视频URL
     */
    extractVideoUrls(decodedCode) {
        if (!decodedCode || typeof decodedCode !== 'string') {
            return [];
        }

        const videoUrls = [];
        
        // 匹配各种视频URL模式
        const patterns = [
            // m3u8文件
            /https?:\/\/[^\s"']+\.m3u8[^\s"']*/gi,
            // ts文件
            /https?:\/\/[^\s"']+\.ts[^\s"']*/gi,
            // mp4文件
            /https?:\/\/[^\s"']+\.mp4[^\s"']*/gi,
            // 其他视频格式
            /https?:\/\/[^\s"']+\.(avi|mov|wmv|flv|webm)[^\s"']*/gi,
            // 包含video关键词的URL
            /https?:\/\/[^\s"']*video[^\s"']*/gi,
            // 包含stream关键词的URL
            /https?:\/\/[^\s"']*stream[^\s"']*/gi,
            // 包含play关键词的URL
            /https?:\/\/[^\s"']*play[^\s"']*/gi
        ];

        patterns.forEach(pattern => {
            const matches = decodedCode.match(pattern);
            if (matches) {
                videoUrls.push(...matches);
            }
        });

        // 去重并过滤
        return [...new Set(videoUrls)].filter(url => {
            // 过滤掉明显不是视频的URL
            const excludePatterns = [
                /\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$/i,
                /googleapis\.com/,
                /cdnjs\.cloudflare\.com/,
                /platform-api\.sharethis\.com/
            ];
            
            return !excludePatterns.some(pattern => pattern.test(url));
        });
    }

    /**
     * 分析HTML文件并解密视频地址
     */
    decode(input) {
        console.log('开始解密视频地址...\n');

        try {
            let htmlContent;
            
            // 检查输入是文件路径还是HTML内容
            if (input.endsWith('.html') || input.includes('<html')) {
                if (fs.existsSync(input)) {
                    console.log(`读取文件: ${input}`);
                    htmlContent = fs.readFileSync(input, 'utf8');
                } else {
                    htmlContent = input;
                }
            } else {
                htmlContent = input;
            }

            // 提取JavaScript Packer代码
            console.log('正在提取JavaScript Packer代码...');
            const packerScripts = this.extractPackerCode(htmlContent);
            
            if (packerScripts.length === 0) {
                console.log('未找到JavaScript Packer代码');
                return this.results;
            }

            console.log(`找到 ${packerScripts.length} 个JavaScript Packer代码块`);

            // 尝试解密每个代码块
            for (let i = 0; i < packerScripts.length; i++) {
                console.log(`正在解密第 ${i + 1} 个代码块...`);
                
                try {
                    const decodedCode = this.decodePackerCode(packerScripts[i]);
                    
                    if (decodedCode) {
                        console.log(`第 ${i + 1} 个代码块解密成功`);
                        this.results.decodedCode = decodedCode;
                        
                        // 提取视频URL
                        const urls = this.extractVideoUrls(decodedCode);
                        this.results.videoUrls.push(...urls);
                        
                        console.log(`从第 ${i + 1} 个代码块中提取到 ${urls.length} 个视频URL`);
                    } else {
                        console.log(`第 ${i + 1} 个代码块解密失败`);
                    }
                } catch (error) {
                    console.log(`第 ${i + 1} 个代码块解密出错: ${error.message}`);
                }
            }

            // 去重视频URL
            this.results.videoUrls = [...new Set(this.results.videoUrls)];

            console.log('\n=== 解密结果 ===');
            console.log(`找到 ${this.results.videoUrls.length} 个视频URL`);
            console.log(`解密了 ${packerScripts.length} 个代码块`);

            if (this.results.videoUrls.length > 0) {
                console.log('\n视频URL列表:');
                this.results.videoUrls.forEach((url, index) => {
                    console.log(`${index + 1}. ${url}`);
                });
            }

            if (this.results.errors.length > 0) {
                console.log('\n错误信息:');
                this.results.errors.forEach(error => {
                    console.log(`- ${error}`);
                });
            }

            // 保存结果
            const outputFile = 'decoded_results.json';
            fs.writeFileSync(outputFile, JSON.stringify(this.results, null, 2));
            console.log(`\n结果已保存到: ${outputFile}`);

            return this.results;

        } catch (error) {
            console.error('解密过程出错:', error.message);
            this.results.errors.push(`解密过程出错: ${error.message}`);
            return this.results;
        }
    }
}

// 如果直接运行此脚本
if (require.main === module) {
    const decoder = new SimpleVideoDecoder();
    
    const input = process.argv[2];
    if (!input) {
        console.log('使用方法: node decoder.js <HTML文件路径或HTML内容>');
        console.log('示例: node decoder.js index.html');
        process.exit(1);
    }

    decoder.decode(input);
}

module.exports = SimpleVideoDecoder; 