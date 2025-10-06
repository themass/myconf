
import requests
import json
import sys

def stream_chat(prompt):
    url = "https://api.doubao.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_API_KEY"  # 替换为你的API密钥
    }
    
    data = {
        "model": "doubao-text",
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }

    try:
        response = requests.post(url, headers=headers, json=data, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                # 移除"data: "前缀并解析JSON
                json_str = line.decode('utf-8').replace("data: ", "")
                if json_str != "[DONE]":
                    try:
                        json_data = json.loads(json_str)
                        if "choices" in json_data and len(json_data["choices"]) > 0:
                            content = json_data["choices"][0].get("delta", {}).get("content", "")
                            if content:
                                sys.stdout.write(content)
                                sys.stdout.flush()
                    except json.JSONDecodeError:
                        continue
        print()  # 打印换行
                
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    while True:
        user_input = input("\n请输入问题 (输入'quit'退出): ")
        if user_input.lower() == 'quit':
            break
        stream_chat(user_input)
