#!/usr/bin/env node

/**
 * 提取HTML中的JavaScript代码
 */

const fs = require('fs');

function extractJavaScriptCode(htmlContent) {
    console.log('开始提取JavaScript代码...');
    
    // 查找所有script标签
    const scriptPattern = /<script[^>]*>([\s\S]*?)<\/script>/gi;
    const scripts = [];
    let match;
    
    while ((match = scriptPattern.exec(htmlContent)) !== null) {
        const scriptContent = match[1].trim();
        if (scriptContent.length > 0) {
            scripts.push({
                content: scriptContent,
                hasEval: scriptContent.includes('eval('),
                hasFunction: scriptContent.includes('function('),
                length: scriptContent.length
            });
        }
    }
    
    console.log(`找到 ${scripts.length} 个script标签`);
    
    // 过滤出包含eval的脚本
    const evalScripts = scripts.filter(script => script.hasEval);
    console.log(`其中 ${evalScripts.length} 个包含eval函数`);
    
    // 保存所有脚本
    const allScripts = {
        total: scripts.length,
        evalScripts: evalScripts.length,
        scripts: scripts
    };
    
    fs.writeFileSync('extracted_scripts.json', JSON.stringify(allScripts, null, 2), 'utf8');
    console.log('脚本内容已保存到 extracted_scripts.json');
    
    // 保存包含eval的脚本到单独文件
    if (evalScripts.length > 0) {
        let evalContent = '';
        evalScripts.forEach((script, index) => {
            evalContent += `// Script ${index + 1}\n`;
            evalContent += script.content + '\n\n';
        });
        
        fs.writeFileSync('eval_scripts.js', evalContent, 'utf8');
        console.log('eval脚本已保存到 eval_scripts.js');
        
        // 尝试提取第一个eval脚本的参数
        const firstEval = evalScripts[0];
        if (firstEval) {
            console.log('\n第一个eval脚本分析:');
            console.log('长度:', firstEval.length);
            console.log('前200字符:', firstEval.content.substring(0, 200));
            
            // 尝试提取eval函数的参数
            const evalMatch = firstEval.content.match(/eval\(function\(p,a,c,k,e,d\)\{([^}]*)\}\(([^)]+)\)\)/);
            if (evalMatch) {
                console.log('\n找到eval函数参数:');
                console.log('函数体:', evalMatch[1]);
                console.log('参数:', evalMatch[2]);
                
                // 保存参数到文件
                fs.writeFileSync('eval_params.txt', evalMatch[2], 'utf8');
                console.log('eval参数已保存到 eval_params.txt');
            }
        }
    }
    
    return allScripts;
}

function main() {
    const args = process.argv.slice(2);
    const htmlFile = args[0] || 'index.html';
    
    try {
        console.log(`读取HTML文件: ${htmlFile}`);
        const htmlContent = fs.readFileSync(htmlFile, 'utf8');
        console.log('HTML文件大小:', htmlContent.length, '字符');
        
        const result = extractJavaScriptCode(htmlContent);
        
        console.log('\n=== 提取完成 ===');
        console.log(`总共提取了 ${result.total} 个脚本`);
        console.log(`其中 ${result.evalScripts} 个包含eval函数`);
        
    } catch (error) {
        console.error('错误:', error.message);
    }
}

if (require.main === module) {
    main();
} 