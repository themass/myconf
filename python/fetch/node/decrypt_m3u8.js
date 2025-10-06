#!/usr/bin/env node

/**
 * JavaScript Packer解密器
 * 专门用于解密JavaScript Packer代码并提取m3u8视频地址
 */

const fs = require('fs');
const vm = require('vm');

class M3U8Decryptor {
    constructor() {
        this.results = {
            m3u8Urls: [],
            videoUrls: [],
            audioUrls: [],
            errors: []
        };
    }

    // 创建完整的浏览器环境模拟
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
                            // 检查写入的内容是否包含m3u8
                            if (content.includes('.m3u8')) {
                                this.extractM3U8FromContent(content);
                            }
                        }
                    };
                    return element;
                },
                getElementById: (id) => null,
                getElementsByTagName: (tag) => [],
                write: (content) => {
                    console.log('document.write:', content);
                    if (content.includes('.m3u8')) {
                        this.extractM3U8FromContent(content);
                    }
                },
                writeln: (content) => {
                    console.log('document.writeln:', content);
                    if (content.includes('.m3u8')) {
                        this.extractM3U8FromContent(content);
                    }
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
                    const result = vm.runInContext(code, context);
                    console.log('eval result:', typeof result, result ? result.substring(0, 100) : 'null');
                    return result;
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

    // 从内容中提取m3u8地址
    extractM3U8FromContent(content) {
        const m3u8Patterns = [
            /https?:\/\/[^\s"']+\.m3u8[^\s"']*/gi,
            /https?:\/\/[^\s"']+\.ts[^\s"']*/gi,
            /https?:\/\/[^\s"']+\.mp4[^\s"']*/gi
        ];

        for (const pattern of m3u8Patterns) {
            const matches = content.match(pattern);
            if (matches) {
                for (const url of matches) {
                    const cleanUrl = url.replace(/['"]/g, '');
                    if (cleanUrl.includes('.m3u8')) {
                        if (!this.results.m3u8Urls.includes(cleanUrl)) {
                            this.results.m3u8Urls.push(cleanUrl);
                            console.log('找到m3u8地址:', cleanUrl);
                        }
                    } else if (cleanUrl.includes('.ts') || cleanUrl.includes('.mp4')) {
                        if (!this.results.videoUrls.includes(cleanUrl)) {
                            this.results.videoUrls.push(cleanUrl);
                            console.log('找到视频地址:', cleanUrl);
                        }
                    }
                }
            }
        }
    }

    // 解密JavaScript Packer代码
    async decryptPackerCode(packerCode) {
        try {
            console.log('开始解密JavaScript Packer代码...');
            console.log('代码长度:', packerCode.length);
            
            const context = this.createBrowserContext();
            
            // 在沙箱环境中执行代码
            const result = vm.runInContext(packerCode, context);
            
            console.log('解密成功，结果类型:', typeof result);
            
            if (typeof result === 'string') {
                console.log('解密结果长度:', result.length);
                console.log('解密结果前200字符:', result.substring(0, 200));
                
                // 从解密结果中提取m3u8地址
                this.extractM3U8FromContent(result);
            }
            
            return result;
            
        } catch (error) {
            console.log('解密失败:', error.message);
            this.results.errors.push(`解密失败: ${error.message}`);
            return null;
        }
    }

    // 解密eval_scripts.js文件
    async decryptEvalScripts() {
        try {
            console.log('读取eval_scripts.js文件...');
            const content = fs.readFileSync('eval_scripts.js', 'utf8');
            
            // 分割脚本
            const scripts = content.split('// Script');
            
            console.log(`找到 ${scripts.length - 1} 个脚本`);
            
            for (let i = 1; i < scripts.length; i++) {
                console.log(`\n=== 解密第 ${i} 个脚本 ===`);
                const scriptContent = scripts[i].trim();
                
                if (scriptContent.includes('eval(function(p,a,c,k,e,d)')) {
                    await this.decryptPackerCode(scriptContent);
                }
            }
            
            return this.results;
            
        } catch (error) {
            console.log('读取文件失败:', error.message);
            this.results.errors.push(`读取文件失败: ${error.message}`);
            return this.results;
        }
    }

    // 保存结果
    saveResults() {
        const outputPath = 'm3u8_decrypt_results.json';
        fs.writeFileSync(outputPath, JSON.stringify(this.results, null, 2), 'utf8');
        console.log(`解密结果已保存到: ${outputPath}`);
    }

    // 打印结果
    printResults() {
        console.log('\n=== M3U8解密结果 ===');
        
        if (this.results.m3u8Urls.length > 0) {
            console.log('\n🎬 M3U8地址:');
            this.results.m3u8Urls.forEach((url, index) => {
                console.log(`${index + 1}. ${url}`);
            });
        }
        
        if (this.results.videoUrls.length > 0) {
            console.log('\n📹 视频地址:');
            this.results.videoUrls.forEach((url, index) => {
                console.log(`${index + 1}. ${url}`);
            });
        }
        
        if (this.results.audioUrls.length > 0) {
            console.log('\n🎵 音频地址:');
            this.results.audioUrls.forEach((url, index) => {
                console.log(`${index + 1}. ${url}`);
            });
        }
        
        if (this.results.errors.length > 0) {
            console.log('\n❌ 错误信息:');
            this.results.errors.forEach((error, index) => {
                console.log(`${index + 1}. ${error}`);
            });
        }
        
        console.log(`\n📊 统计信息:`);
        console.log(`- M3U8地址: ${this.results.m3u8Urls.length} 个`);
        console.log(`- 视频地址: ${this.results.videoUrls.length} 个`);
        console.log(`- 音频地址: ${this.results.audioUrls.length} 个`);
        console.log(`- 错误数量: ${this.results.errors.length} 个`);
    }
}

// 主函数
async function main() {
    const decryptor = new M3U8Decryptor();
    
    console.log('🎬 M3U8地址解密器');
    console.log('==================');
    
    // 解密eval_scripts.js文件
    await decryptor.decryptEvalScripts();
    
    // 保存结果
    decryptor.saveResults();
    
    // 打印结果
    decryptor.printResults();
}

// 如果直接运行此脚本
if (require.main === module) {
    main().catch(console.error);
}

module.exports = M3U8Decryptor; 