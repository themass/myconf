#!/usr/bin/env node

/**
 * JavaScript视频地址解密工具
 * 专门用于解密JavaScript Packer加密的视频地址
 */

const fs = require('fs');
const vm = require('vm');

class VideoDecoder {
    constructor() {
        this.decodedResults = [];
        this.videoUrls = [];
    }

    /**
     * 解密JavaScript Packer代码
     * @param {string} jsCode - 加密的JavaScript代码
     * @returns {string|null} 解密后的代码
     */
    decodePacker(jsCode) {
        try {
            // 创建安全的执行环境
            const context = {
                console: {
                    log: (...args) => {
                        console.log('JS Console:', ...args);
                    }
                },
                document: {
                    createElement: () => ({}),
                    getElementById: () => null,
                    getElementsByTagName: () => []
                },
                window: {},
                location: {
                    host: 'localhost',
                    href: 'http://localhost'
                },
                navigator: {
                    userAgent: 'Mozilla/5.0 (Node.js)',
                    languages: ['zh-CN', 'zh', 'en']
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
                String: {
                    fromCharCode: String.fromCharCode
                },
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
            console.error('解密失败:', error.message);
            return null;
        }
    }

    /**
     * 从解密后的代码中提取视频URL
     * @param {string} decodedCode - 解密后的代码
     * @returns {Array} 视频URL数组
     */
    extractVideoUrls(decodedCode) {
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
     * 分析HTML文件中的JavaScript代码
     * @param {string} htmlContent - HTML内容
     * @returns {Object} 分析结果
     */
    analyzeHtml(htmlContent) {
        const results = {
            packerScripts: [],
            videoUrls: [],
            decodedCode: []
        };

        // 查找JavaScript Packer代码
        let packerMatches = htmlContent.match(/<script[^>]*>eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*d\s*\)\s*\{[^}]*\}\s*\([^)]+\)\s*\)[^<]*<\/script>/g);
        
        // 如果上面的正则表达式没有匹配到，尝试更宽松的匹配
        if (!packerMatches || packerMatches.length === 0) {
            packerMatches = htmlContent.match(/eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*d\s*\)\s*\{[^}]*\}\s*\([^)]+\)\s*\)/g);
        }

        if (packerMatches) {
            console.log(`找到 ${packerMatches.length} 个JavaScript Packer代码块`);
            
            packerMatches.forEach((match, index) => {
                console.log(`\n正在解密第 ${index + 1} 个代码块...`);
                
                try {
                    const decodedCode = this.decodePacker(match);
                    if (decodedCode) {
                        results.decodedCode.push(decodedCode);
                        
                        // 提取视频URL
                        const urls = this.extractVideoUrls(decodedCode);
                        if (urls.length > 0) {
                            console.log(`找到 ${urls.length} 个视频URL:`);
                            urls.forEach(url => console.log(`  - ${url}`));
                            results.videoUrls.push(...urls);
                        }
                    }
                } catch (error) {
                    console.error(`解密第 ${index + 1} 个代码块失败:`, error.message);
                }
            });
        }

        // 去重
        results.videoUrls = [...new Set(results.videoUrls)];
        
        return results;
    }

    /**
     * 主解密函数
     * @param {string} input - 输入内容（可以是HTML文件路径或JavaScript代码）
     * @returns {Object} 解密结果
     */
    decode(input) {
        console.log('开始解密视频地址...\n');

        let htmlContent = '';
        
        // 检查输入是文件路径还是代码内容
        if (fs.existsSync(input)) {
            console.log(`读取文件: ${input}`);
            htmlContent = fs.readFileSync(input, 'utf8');
        } else {
            console.log('使用输入的代码内容');
            htmlContent = input;
        }

        const results = this.analyzeHtml(htmlContent);
        
        console.log('\n=== 解密结果 ===');
        console.log(`找到 ${results.videoUrls.length} 个视频URL`);
        console.log(`解密了 ${results.decodedCode.length} 个代码块`);
        
        if (results.videoUrls.length > 0) {
            console.log('\n视频URL列表:');
            results.videoUrls.forEach((url, index) => {
                console.log(`${index + 1}. ${url}`);
            });
        }

        return results;
    }
}

// 如果直接运行此脚本
if (require.main === module) {
    const decoder = new VideoDecoder();
    
    // 获取命令行参数
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.log('使用方法: node index.js <HTML文件路径或JavaScript代码>');
        console.log('示例: node index.js index.html');
        console.log('示例: node index.js "eval(function(p,a,c,k,e,d){...})"');
        process.exit(1);
    }

    const input = args[0];
    const results = decoder.decode(input);
    
    // 保存结果到文件
    const outputFile = 'decoded_results.json';
    fs.writeFileSync(outputFile, JSON.stringify(results, null, 2));
    console.log(`\n结果已保存到: ${outputFile}`);
}

module.exports = VideoDecoder; 