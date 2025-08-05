// unpack.js
const fs = require('fs');
const vm = require('vm');

// 读取原始代码
const jsCode = fs.readFileSync('original.js', 'utf8');

// 创建一个沙箱环境
const sandbox = {
    console: console,
    B: "B", // 需要根据实际情况替换
    A: "A",
    z: 6,
    y: ""
};

vm.createContext(sandbox);

// 执行解包
const result = vm.runInContext(jsCode, sandbox);
console.log(result);