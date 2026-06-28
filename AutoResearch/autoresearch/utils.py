"""
工具函数模块
"""
import re
from typing import List, Dict, Any


def extract_citations(text: str) -> List[str]:
    """从文本中提取引用"""
    # 匹配常见的引用格式
    patterns = [
        r'\[.*?\]\(.*?\)',  # Markdown 链接
        r'\(.*?https?://.*?\)',  # 括号内的 URL
        r'https?://[^\s\)]+',  # 直接的 URL
    ]

    citations = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        citations.extend(matches)

    return list(set(citations))  # 去重


def format_token_usage(usage: Dict) -> str:
    """格式化 token 使用信息"""
    if not usage:
        return "N/A"

    prompt = usage.get("prompt_tokens", 0)
    completion = usage.get("completion_tokens", 0)
    total = usage.get("total_tokens", prompt + completion)

    reasoning = usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0)

    lines = [
        f"Prompt: {prompt:,}",
        f"Completion: {completion:,}",
    ]

    if reasoning:
        lines.append(f"Reasoning: {reasoning:,}")

    lines.append(f"Total: {total:,}")

    return " | ".join(lines)


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def clean_markdown(text: str) -> str:
    """清理 Markdown 文本"""
    # 移除过多的空行
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 统一标题格式
    text = re.sub(r'^(#{1,6})\s*', r'\1 ', text, flags=re.MULTILINE)

    return text.strip()


def extract_key_points(content: str) -> List[str]:
    """提取关键点"""
    key_points = []

    # 尝试提取列表项
    list_items = re.findall(r'^[\-\*\+]\s+(.+)$', content, re.MULTILINE)
    if list_items:
        key_points.extend(list_items[:5])  # 最多取 5 个

    # 如果没有列表，尝试提取句子
    if not key_points:
        sentences = re.split(r'[。！？\n]', content)
        key_points = [s.strip() for s in sentences if len(s.strip()) > 10][:5]

    return key_points


def calculate_relevance_score(topic: str, content: str) -> float:
    """计算内容相关性分数"""
    topic_words = set(topic.lower().split())
    content_words = set(content.lower().split())

    if not topic_words:
        return 0.0

    intersection = topic_words & content_words
    union = topic_words | content_words

    return len(intersection) / len(union) if union else 0.0


def merge_results(results: List[Dict[str, Any]], key: str = "content") -> str:
    """合并多个结果"""
    merged = []

    for i, result in enumerate(results, 1):
        content = result.get(key, "")
        if content:
            merged.append(f"## 部分 {i}\n\n{content}")

    return "\n\n---\n\n".join(merged)
