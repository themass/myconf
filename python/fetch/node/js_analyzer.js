#!/usr/bin/env node

/**
 * JavaScript加密代码分析器
 * 专门用于分析HTML中的JavaScript Packer加密代码
 */

const fs = require('fs');
const vm = require('vm');

class JavaScriptAnalyzer {
    constructor() {
        this.results = {
            videoUrls: [],
            audioUrls: [],
            decodedCode: null,
            errors: []
        };
    }

    // 提取HTML中的JavaScript Packer代码
    extractPackerCode(htmlContent) {
        const packerPatterns = [
            // 匹配完整的script标签中的eval函数
            /<script>eval\(function\(p,a,c,k,e,d\)\{[^}]*\}\([^)]+\)\)<\/script>/g,
            // 匹配单独的eval函数（可能被截断）
            /eval\(function\(p,a,c,k,e,d\)\{[^}]*\}\([^)]+\)\)/g,
            // 匹配被截断的eval函数开始
            /eval\(function\(p,a,c,k,e,d\)\{[^}]*\}/g,
            // 更宽松的匹配，查找包含eval和function的script标签
            /<script>[^<]*eval[^<]*function[^<]*<\/script>/g
        ];

        const packerCodes = [];
        
        for (const pattern of packerPatterns) {
            const matches = htmlContent.match(pattern);
            if (matches) {
                packerCodes.push(...matches);
            }
        }

        // 如果没有找到完整的代码，尝试手动提取
        if (packerCodes.length === 0) {
            console.log('尝试手动提取JavaScript Packer代码...');
            
            // 查找包含eval的script标签
            const scriptMatches = htmlContent.match(/<script>([^<]+)<\/script>/g);
            if (scriptMatches) {
                for (const script of scriptMatches) {
                    if (script.includes('eval(function(p,a,c,k,e,d)')) {
                        packerCodes.push(script);
                    }
                }
            }
        }

        return packerCodes;
    }

    // 创建更完整的浏览器环境模拟
    createBrowserContext() {
        const context = {
            console: {
                log: (...args) => {
                    console.log('JS Console:', ...args);
                },
                error: (...args) => {
                    console.log('JS Error:', ...args);
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
                        setAttribute: (name, value) => {
                            element[name] = value;
                        },
                        getAttribute: (name) => element[name] || null,
                        appendChild: (child) => {},
                        removeChild: (child) => {},
                        write: (content) => {
                            console.log('document.write:', content);
                        }
                    };
                    return element;
                },
                getElementById: (id) => null,
                getElementsByTagName: (tag) => [],
                write: (content) => {
                    console.log('document.write:', content);
                },
                writeln: (content) => {
                    console.log('document.writeln:', content);
                },
                body: {
                    appendChild: (child) => {},
                    innerHTML: ''
                },
                head: {
                    appendChild: (child) => {}
                }
            },
            window: {
                document: null,
                location: null,
                navigator: null,
                innerHeight: 768,
                innerWidth: 1024,
                outerHeight: 768,
                outerWidth: 1024,
                screenX: 0,
                screenY: 0,
                scrollX: 0,
                scrollY: 0,
                pageXOffset: 0,
                pageYOffset: 0,
                screen: {
                    width: 1024,
                    height: 768,
                    availWidth: 1024,
                    availHeight: 768,
                    colorDepth: 24,
                    pixelDepth: 24
                }
            },
            location: {
                host: 'localhost',
                href: 'http://localhost',
                protocol: 'http:',
                hostname: 'localhost',
                port: '',
                pathname: '/',
                search: '',
                hash: '',
                origin: 'http://localhost',
                assign: (url) => {
                    console.log('location.assign:', url);
                },
                reload: () => {
                    console.log('location.reload');
                },
                replace: (url) => {
                    console.log('location.replace:', url);
                }
            },
            navigator: {
                userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                languages: ['zh-CN', 'zh', 'en'],
                platform: 'Win32',
                cookieEnabled: true,
                onLine: true,
                appName: 'Netscape',
                appVersion: '5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                appCodeName: 'Mozilla',
                product: 'Gecko',
                productSub: '20030107',
                vendor: 'Google Inc.',
                vendorSub: '',
                maxTouchPoints: 0,
                hardwareConcurrency: 8,
                deviceMemory: 8,
                connection: {
                    effectiveType: '4g',
                    rtt: 50,
                    downlink: 10,
                    saveData: false
                }
            },
            videojs: {
                getPlugin: (name) => ({
                    version: '1.0.0',
                    name: name
                }),
                registerPlugin: (name, plugin) => {
                    console.log('videojs.registerPlugin:', name);
                },
                getPluginVersion: (name) => '1.0.0',
                VERSION: '7.20.3'
            },
            String: String,
            Number: Number,
            Boolean: Boolean,
            Array: Array,
            Object: Object,
            Function: Function,
            RegExp: RegExp,
            Date: Date,
            Math: Math,
            JSON: JSON,
            parseInt: parseInt,
            parseFloat: parseFloat,
            isNaN: isNaN,
            isFinite: isFinite,
            escape: escape,
            unescape: unescape,
            encodeURI: encodeURI,
            encodeURIComponent: encodeURIComponent,
            decodeURI: decodeURI,
            decodeURIComponent: decodeURIComponent,
            eval: (code) => {
                try {
                    return vm.runInContext(code, context);
                } catch (e) {
                    console.log('eval error:', e.message);
                    return undefined;
                }
            },
            setTimeout: (func, delay) => {
                console.log('setTimeout called with delay:', delay);
            },
            setInterval: (func, delay) => {
                console.log('setInterval called with delay:', delay);
            },
            clearTimeout: () => {},
            clearInterval: () => {},
            alert: (msg) => {
                console.log('alert:', msg);
            },
            confirm: (msg) => {
                console.log('confirm:', msg);
                return true;
            },
            prompt: (msg, defaultValue) => {
                console.log('prompt:', msg, defaultValue);
                return defaultValue || '';
            }
        };

        // 设置循环引用
        context.window.document = context.document;
        context.window.location = context.location;
        context.window.navigator = context.navigator;
        context.document.defaultView = context.window;

        return context;
    }

    // 解密JavaScript Packer代码
    async decodePackerCode(packerCode) {
        try {
            console.log('开始解密JavaScript Packer代码...');
            
            const context = this.createBrowserContext();
            
            // 在沙箱环境中执行代码
            const result = vm.runInContext(packerCode, context);
            
            console.log('解密成功，结果类型:', typeof result);
            
            if (typeof result === 'string') {
                console.log('解密结果长度:', result.length);
                console.log('解密结果前200字符:', result.substring(0, 200));
                
                // 从解密结果中提取视频和音频URL
                this.extractUrlsFromDecoded(result);
            }
            
            return result;
            
        } catch (error) {
            console.log('解密失败:', error.message);
            this.results.errors.push(`解密失败: ${error.message}`);
            return null;
        }
    }

    // 从解密结果中提取URL
    extractUrlsFromDecoded(decodedCode) {
        const urlPatterns = [
            /https?:\/\/[^\s"']+\.m3u8[^\s"']*/gi,
            /https?:\/\/[^\s"']+\.ts[^\s"']*/gi,
            /https?:\/\/[^\s"']+\.mp4[^\s"']*/gi,
            /https?:\/\/[^\s"']+\.mp3[^\s"']*/gi,
            /https?:\/\/[^\s"']+\.wav[^\s"']*/gi,
            /https?:\/\/[^\s"']+\.aac[^\s"']*/gi,
            /https?:\/\/[^\s"']+video[^\s"']*/gi,
            /https?:\/\/[^\s"']+audio[^\s"']*/gi,
            /https?:\/\/[^\s"']+stream[^\s"']*/gi,
            /https?:\/\/[^\s"']+play[^\s"']*/gi
        ];

        for (const pattern of urlPatterns) {
            const matches = decodedCode.match(pattern);
            if (matches) {
                for (const url of matches) {
                    const cleanUrl = url.replace(/['"]/g, '');
                    
                    if (cleanUrl.includes('.m3u8') || cleanUrl.includes('.ts') || cleanUrl.includes('.mp4')) {
                        if (!this.results.videoUrls.includes(cleanUrl)) {
                            this.results.videoUrls.push(cleanUrl);
                        }
                    } else if (cleanUrl.includes('.mp3') || cleanUrl.includes('.wav') || cleanUrl.includes('.aac')) {
                        if (!this.results.audioUrls.includes(cleanUrl)) {
                            this.results.audioUrls.push(cleanUrl);
                        }
                    }
                }
            }
        }
    }

    // 分析HTML文件
    async analyzeHtmlFile(filePath) {
        try {
            console.log(`分析HTML文件: ${filePath}`);
            
            const htmlContent = fs.readFileSync(filePath, 'utf8');
            console.log('HTML文件大小:', htmlContent.length, '字符');
            
            // 提取JavaScript Packer代码
            const packerCodes = this.extractPackerCode(htmlContent);
            console.log(`找到 ${packerCodes.length} 个JavaScript Packer代码块`);
            
            // 解密每个代码块
            for (let i = 0; i < packerCodes.length; i++) {
                console.log(`\n=== 解密第 ${i + 1} 个代码块 ===`);
                const decoded = await this.decodePackerCode(packerCodes[i]);
                if (decoded) {
                    this.results.decodedCode = decoded;
                }
            }
            
            // 保存结果
            this.saveResults();
            
            return this.results;
            
        } catch (error) {
            console.log('分析失败:', error.message);
            this.results.errors.push(`分析失败: ${error.message}`);
            return this.results;
        }
    }

    // 保存分析结果
    saveResults() {
        const outputPath = 'js_analysis_results.json';
        fs.writeFileSync(outputPath, JSON.stringify(this.results, null, 2), 'utf8');
        console.log(`分析结果已保存到: ${outputPath}`);
    }

    // 打印分析结果
    printResults() {
        console.log('\n=== JavaScript分析结果 ===');
        
        if (this.results.videoUrls.length > 0) {
            console.log('\n视频URL:');
            this.results.videoUrls.forEach((url, index) => {
                console.log(`${index + 1}. ${url}`);
            });
        }
        
        if (this.results.audioUrls.length > 0) {
            console.log('\n音频URL:');
            this.results.audioUrls.forEach((url, index) => {
                console.log(`${index + 1}. ${url}`);
            });
        }
        
        if (this.results.errors.length > 0) {
            console.log('\n错误信息:');
            this.results.errors.forEach((error, index) => {
                console.log(`${index + 1}. ${error}`);
            });
        }
        
        console.log(`\n总共找到 ${this.results.videoUrls.length} 个视频URL`);
        console.log(`总共找到 ${this.results.audioUrls.length} 个音频URL`);
    }
}

// 主函数
async function main() {
    const analyzer = new JavaScriptAnalyzer();
    
    // 检查命令行参数
    const args = process.argv.slice(2);
    const htmlFile = args[0] || 'index.html';
    
    console.log('JavaScript加密代码分析器');
    console.log('========================');
    
    // 分析HTML文件
    await analyzer.analyzeHtmlFile(htmlFile);
    
    // 打印结果
    analyzer.printResults();
}

// 如果直接运行此脚本
if (require.main === module) {
    main().catch(console.error);
}

module.exports = JavaScriptAnalyzer; 