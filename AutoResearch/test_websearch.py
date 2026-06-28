"""
测试 deepseek-v4-pro 的 websearch 功能
"""
import os
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

API_KEY = os.getenv("apikey")
BASE_URL = os.getenv("base", "https://api.deepseek.com")
MODEL = os.getenv("model", "deepseek-v4-pro")

print(f"API Key: {API_KEY[:20]}...")
print(f"Base URL: {BASE_URL}")
print(f"Model: {MODEL}")
print("-" * 50)

# 测试 websearch 功能
url = f"{BASE_URL}/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 测试问题 - 需要实时信息的问题
test_question = "2025年最新的AI模型发布情况如何？"

payload = {
    "model": MODEL,
    "messages": [
        {
            "role": "user",
            "content": test_question
        }
    ],
    "web_search": True  # 启用 websearch
}

print(f"测试问题: {test_question}")
print("\n发送请求...")

try:
    response = requests.post(url, headers=headers, json=payload, timeout=60)

    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\n" + "=" * 60)
        print("响应成功!")
        print("=" * 60)

        # 打印完整响应用于调试
        print("\n完整响应:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # 提取回答
        if "choices" in result and len(result["choices"]) > 0:
            answer = result["choices"][0]["message"]["content"]
            print("\n" + "=" * 60)
            print("AI 回答:")
            print("=" * 60)
            print(answer)

        # 检查是否有 websearch 相关信息
        if "web_search" in result.get("usage", {}):
            print("\n" + "=" * 60)
            print("WebSearch 使用信息:")
            print("=" * 60)
            print(json.dumps(result["usage"]["web_search"], indent=2, ensure_ascii=False))
    else:
        print(f"\n请求失败!")
        print(f"响应内容: {response.text}")

except requests.exceptions.Timeout:
    print("\n请求超时!")
except requests.exceptions.RequestException as e:
    print(f"\n请求异常: {e}")
except Exception as e:
    print(f"\n未知错误: {e}")
