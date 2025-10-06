#!/usr/bin/env node

/**
 * 测试脚本
 * 用于测试视频解密功能
 */

const VideoDecoder = require('./index.js');
const fs = require('fs');

// 测试用的JavaScript Packer代码片段
const testPackerCode = `
eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('6 5=["","U","T+/","S","R","","",".","Q","P","O","0"];m p(d,e,f){6 g=5[2][5[1]](5[0]);6 h=g[5[3]](0,e);6 i=g[5[3]](0,f);6 j=d[5[1]](5[0])[5[o]]()[5[9]](m(a,b,c){N(h[5[4]](b)!==-1)l a+=h[5[4]](b)*(M[5[8]](e,c))},0);6 k=5[0];w(j>0){k=i[j%f]+k;j=(j-(j%f))/f}l k||5[L]}K(m(h,u,n,t,e,r){r="";v(6 i=0,x=h.q;i<x;i++){6 s="";w(h[i]!==n[e]){s+=h[i];i++}v(6 j=0;j<n.q;j++)s=s.J(I H(n[j],"g"),j);r+=G.F(p(s,e,o)-t)}l E(D(r))}("C",B,"A",z,7,y))',57,57,'|||||_0xc26e|var|||||||||||||||return|function||10|_0xe73c|length|||||for|while|len|29|49|xeOBLFguS|68|BxOuBeguBxeuBOFuBeLuBxBuBeFuBOLuegLuBBxuBOOuBexuBOLuBxBueFFueFLuOeLuBxOuBexuBOgueLLuBOBuBOLuBBOuBeBuBxBuOeFuOgeueFLuBOxuBeguBOBuBexuBOLuBexuBeguBeFuOeOuBOOuBxBuBeBuOgguBOLuBexuBOguBxBuOgeueFLuOegueLLuOeLuBOguBexuBxOuBxBuBeguegBuBeeuBOBueLLuBexuBxOuOeFuOgeueFLuBeLuBBOuBOguBexuBxOuBxBuBeguOgeueFLueLLuBxeuBeBuOgguBOBuBOBuOeFuOgeueLguBOguBexuBxOuBxBuBeguegBuBeeuBOBueLLuBOguBeeuBOBuegBuOxxuOxFuegBuOeeueLLuBOguBeeuBOBuegBuBOLuBxguBxBuBeLuBxBuegBuBxeuBexuBOLuBBOuOgeueLgueLLuBOxuBeBuOgguBBOuBOBuOBBuBeFuBeBuBexuBeFuBxBuOeFuOgeueLguBOLuBOOuBOFuBxBuOgeueLgueLLuBxeuBeguBeFuBOLuBOOuBeguBeBuBOBueLLuBBeuegBuBBxuBxBuBxxuBeOuBexuBOLuegBuOgguBexuBOOuBOxuBeBuOgguBBOuOeFuOgeueLguOgguBeBuBeBuBeguBBxuOgeueLgueLLuBBxuBxBuBxxuBeOuBexuBOLuegBuBOxuBeBuOgguBBOuBOBuBexuBeFuBeBuBexuBeFuBxBueLLuOeguOeLuegFuBOguBexuBxOuBxBuBeguegBuBeeuBOBuOegueLLuOeLuBxOuBexuBOgueLLuBexuBxOuOeFuOgeueLguBOLuBeguOgguBOBuBOLuOgeueLgueLLuBxeuBeBuOgguBOBuBOBuOeFuOgeueLguBOLuBeguOgguBOBuBOLuOgeueLguOeguOeLuegFuBxOuBexuBOguOeguOeLuegFuBxOuBexuBOguOeguOeLuBxOuBexuBOgueLLuBxeuBeBuOgguBOBuBOBuOeFuOgeueLguBOLuBxBuBBeuBOLuegBuBxeuBxBuBeFuBOLuBxBuBOOuOgeueLguOeguOeLuBxOuBexuBOgueLLuBxeuBeBuOgguBOBuBOBuOeFuOgeueLguBxxuBOLuBeFuegBuBxFuBOOuBeguBOFuBOxueLLuBxOuegBuBxLuBeBuBxBuBBeueLLuBeeuBOFuBOBuBOLuBexuBxLuBBOuegBuBxeuBeguBeFuBOLuBxBuBeFuBOLuegBuBxeuBxBuBeFuBOLuBxBuBOOueLLuBBxuegBuOxxueggueggueLLuBOguBexuBxOuBxBuBeguegBuBxeuBeguBeFuBOLuBOOuBeguBeBuOgeueLguOeguOeLuBxxuBOFuBOLuBOLuBeguBeFueLLuBOLuBBOuBOxuBxBuOeFuOgeueLguBxxuBOFuBOLuBOLuBeguBeFuOgeueLgueLLuBxeuBeBuOgguBOBuBOBuOeFuOgeueLguBxxuBOLuBeFueLLuBxxuBOLuBeFuegBuBxOuOgguBOOuBeOueLLuBxxuBOLuBeFuegBuBxLuBeguBOOuBBxuOgguBOOuBxOueLLuBxOuegBuBeFuBeguBeFuBxBueLLuBxOuegBuBOBuBeLuegBuBexuBeFuBeBuBexuBeFuBxBuegBuBxxuBeBuBeguBxeuBeOuOgeueLgueLLuBxOuOgguBOLuOgguegBuBxLuBeguBOOuBBxuOgguBOOuBxOuOeFuOgeueLguegBuOxxuegguOgeueLguOeguegBuOxxuegguBOBueLLuOeLuegFuBxxuBOFuBOLuBOLuBeguBeFuOegueLLuOeLuBxxuBOFuBOLuBOLuBeguBeFueLLuBOLuBBOuBOxuBxBuOeFuOgeueLguBxxuBOFuBOLuBOLuBeguBeFuOgeueLgueLLuBxeuBeBuOgguBOBuBOBuOeFuOgeueLguBxxuBOLuBeFueLLuBxxuBOLuBeFuegBuBxOuOgguBOOuBeOueLLuBxxuBOLuBeFuegBuBxLuBeguBOOuBBxuOgguBOOuBxOueLLuOgeueLgueLLuBxOuOgguBOLuOgguegBuBxLuBeguBOOuBBxuOgguBOOuBxOuOeFuOgeueLguOxxuegguOgeueLguOeguegeuOxxuegguBOBueLLuOeLuegFuBxxuBOFuBOLuBOLuBeguBeFuOegueLLuOeLuOggueLLuBxeuBeBuOgguBOBuBOBuOeFuOgeueLguBxxuBOLuBeFueLLuBxxuBOLuBeFuegBuBxOuOgguBOOuBeOuOgeueLgueLLuBxguBOOuBxBuBxLuOeFuOgeueLguegFuBOguegFuOexuBOeuOLxuOeeuOOFuOLxuOgeueLguOeguOeLuBexueLLuBxeuBeBuOgguBOBuBOBuOeFuOgeueFLuBxLuOggueLLuBxLuOgguegBuBOBuBOLuBxBuBOxuegBuBxLuBeguBOOuBBxuOgguBOOuBxOuOgeueFLuOeguOeLuegFuBexuOegueLLuOeLuBOBuBOxuOgguBeFueLLuBxeuBeBuOgguBOBuBOBuOeFuOgeueLguBxOuegBuBeFuBeguBeFuBxBueLLuBxOuegBuBOBuBeLuegBuBexuBeFuBeBuBexuBeFuBxBuegBuBxxuBeBuBeguBxeuBeOuOgeueLguOeguFLLuLFOuBFguFFOuLeeuBFeuOeLuegFuBOBuBOxuOgguBeFuOeguOeLuegFuOgguOeguOeLuegFuBxOuBexuBOguOeguOeLuegFuBxOuBexuBOguOegueLLueFLueFguOeBu|escape|decodeURIComponent|fromCharCode|String|RegExp|new|replace|eval|11|Math|if|reverse|reduce|pow|indexOf|slice|0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ|split'.split('|'),0,{}))
`;

function runTests() {
    console.log('=== 开始测试视频解密功能 ===\n');
    
    const decoder = new VideoDecoder();
    
    // 测试1: 测试HTML文件
    console.log('测试1: 分析HTML文件');
    if (fs.existsSync('index.html')) {
        const results1 = decoder.decode('index.html');
        console.log('HTML文件测试完成\n');
    } else {
        console.log('HTML文件不存在，跳过测试1\n');
    }
    
    // 测试2: 测试JavaScript Packer代码
    console.log('测试2: 解密JavaScript Packer代码');
    try {
        const results2 = decoder.decode(testPackerCode);
        console.log('JavaScript Packer代码测试完成\n');
    } catch (error) {
        console.error('JavaScript Packer代码测试失败:', error.message, '\n');
    }
    
    // 测试3: 测试URL提取功能
    console.log('测试3: 测试URL提取功能');
    const testDecodedCode = `
        var videoUrl1 = "https://example.com/video1.m3u8";
        var videoUrl2 = "https://example.com/video2.ts";
        var videoUrl3 = "https://example.com/video3.mp4";
        var cssUrl = "https://example.com/style.css";
    `;
    
    const urls = decoder.extractVideoUrls(testDecodedCode);
    console.log(`提取到 ${urls.length} 个视频URL:`);
    urls.forEach((url, index) => {
        console.log(`${index + 1}. ${url}`);
    });
    console.log('URL提取测试完成\n');
    
    console.log('=== 所有测试完成 ===');
}

// 运行测试
if (require.main === module) {
    runTests();
}

module.exports = { runTests }; 