#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

def filter_to_chinese_english_digits(text):
    """
    过滤字符串，仅保留：
    - 中文（\u4e00-\u9fa5）
    - 英文（大小写字母 a-zA-Z）
    - 数字（0-9）
    移除所有其他字符
    """
    if not text:
        return u""  # 返回空的Unicode字符串

    # 1. 确保输入为Unicode（处理Python 2.7的str/unicode差异）
    if isinstance(text, str):
        # 尝试用utf-8解码，失败则忽略错误字符
        text = text.decode('utf-8', errors='ignore')
    elif not isinstance(text, unicode):
        return u""  # 非字符串类型直接返回空

    # 2. 正则匹配：只保留中文、英文和数字
    # [\u4e00-\u9fa5] 匹配所有中文字符
    # [a-zA-Z] 匹配所有英文字母（大小写）
    # [0-9] 匹配所有数字
    pattern = re.compile(u'([\u4e00-\u9fa5a-zA-Z0-9])')

    # 3. 提取所有匹配的字符并拼接
    filtered_chars = pattern.findall(text)
    filtered_text = u''.join(filtered_chars)

    return filtered_text

# 测试示例
if __name__ == "__main__":
    test_cases = [
        u"测试123！Hello World@#$",
        u"Python 2.7 转义字符串，只保留中文，英文和数字，其他字符全部去掉。",
        u"❌❌⭕️⭕️ 🩷 wataa🔥porn(twitter.com) 测试123！",
        "混合str类型的文本：abc123，中文测试！"  # str类型测试
    ]

    for i, case in enumerate(test_cases):
        result = filter_to_chinese_english_digits(case)
        print(u"测试案例 %d：" % (i+1))
        print(u"原始文本：%s" % case)
        print(u"过滤后：%s\n" % result)
