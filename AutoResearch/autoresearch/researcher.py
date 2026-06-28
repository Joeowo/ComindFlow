"""
核心研究模块
使用 DeepSeek API 进行自动化研究
"""
import requests
import json
import time
from typing import Dict, List, Optional, Generator
from dataclasses import dataclass, field
from datetime import datetime

from .config import Config


@dataclass
class SearchQuery:
    """搜索查询"""
    query: str
    context: str = ""
    depth: str = "comprehensive"  # basic, standard, comprehensive


@dataclass
class ResearchResult:
    """研究结果"""
    topic: str
    content: str
    reasoning: str = ""
    sources: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    token_usage: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "topic": self.topic,
            "content": self.content,
            "reasoning": self.reasoning,
            "sources": self.sources,
            "timestamp": self.timestamp,
            "token_usage": self.token_usage,
        }


class DeepSeekResearcher:
    """DeepSeek 研究器"""

    def __init__(self, config: Config = None):
        self.config = config or Config
        self.api_key = self.config.API_KEY
        self.base_url = self.config.BASE_URL
        self.model = self.config.MODEL
        self.endpoint = f"{self.base_url}/chat/completions"

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _make_request(
        self,
        messages: List[Dict],
        web_search: bool = True,
        max_tokens: int = None,
        **kwargs
    ) -> Dict:
        """发起 API 请求"""
        payload = {
            "model": self.model,
            "messages": messages,
            "web_search": web_search,
            **kwargs
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        for attempt in range(Config.MAX_RETRIES):
            try:
                response = requests.post(
                    self.endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=Config.TIMEOUT
                )
                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                print(f"请求超时，重试 {attempt + 1}/{Config.MAX_RETRIES}...")
                time.sleep(2 ** attempt)

            except requests.exceptions.RequestException as e:
                if attempt == Config.MAX_RETRIES - 1:
                    raise Exception(f"API 请求失败: {e}")
                print(f"请求失败，重试 {attempt + 1}/{Config.MAX_RETRIES}...")
                time.sleep(2 ** attempt)

        return {}

    def search(self, query: SearchQuery) -> ResearchResult:
        """执行单次搜索"""
        print(f"\n🔍 搜索: {query.query}")

        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt(query.depth)
            },
            {
                "role": "user",
                "content": self._format_user_query(query)
            }
        ]

        result = self._make_request(messages, web_search=Config.WEB_SEARCH_ENABLED)

        return self._parse_result(query.query, result)

    def research_deep(
        self,
        topic: str,
        aspects: List[str],
        depth: str = "comprehensive"
    ) -> List[ResearchResult]:
        """深度研究：分多个维度进行研究"""
        print(f"\n📚 开始深度研究: {topic}")
        print(f"研究维度: {', '.join(aspects)}")

        results = []

        for i, aspect in enumerate(aspects, 1):
            print(f"\n{'='*60}")
            print(f"维度 {i}/{len(aspects)}: {aspect}")
            print(f"{'='*60}")

            query = SearchQuery(
                query=f"{topic} - {aspect}",
                context=f"专注于 {aspect} 方面的研究",
                depth=depth
            )

            result = self.search(query)
            results.append(result)

        return results

    def research_iterative(
        self,
        topic: str,
        questions: List[str],
        previous_context: str = ""
    ) -> Generator[ResearchResult, None, None]:
        """迭代研究：基于上下文逐步深入研究"""
        context = previous_context

        for i, question in enumerate(questions, 1):
            print(f"\n{'='*60}")
            print(f"问题 {i}/{len(questions)}: {question}")
            print(f"{'='*60}")

            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的研究助手，擅长深入分析问题并提供详尽的答案。"
                },
            ]

            if context:
                messages.append({
                    "role": "assistant",
                    "content": f"之前的研究结果：\n\n{context}\n\n请基于这些信息继续研究。"
                })

            messages.append({
                "role": "user",
                "content": question
            })

            result_dict = self._make_request(messages, web_search=True)
            result = self._parse_result(question, result_dict)

            context += f"\n\n## {question}\n\n{result.content}"
            yield result

    def generate_research_questions(
        self,
        topic: str,
        research_type: str = "通用"
    ) -> List[str]:
        """生成研究问题列表"""
        print(f"\n🤔 为 '{topic}' 生成研究问题...")

        template = Config.RESEARCH_TEMPLATES.get(research_type, Config.RESEARCH_TEMPLATES["通用"])

        prompt = f"""请为主题 "{topic}" 生成一组深度研究问题。

研究类型: {research_type}
研究描述: {template['description']}
重点关注: {', '.join(template['focus_areas'])}

请生成 5-8 个具体的研究问题，这些问题应该：
1. 覆盖主题的各个重要方面
2. 从基础到深入，循序渐进
3. 具有实际的研究价值
4. 便于通过搜索获得答案

只返回问题列表，每行一个问题，以数字编号。"""

        messages = [
            {"role": "system", "content": "你是一个专业的研究策划专家。"},
            {"role": "user", "content": prompt}
        ]

        result = self._make_request(messages, web_search=True, max_tokens=1000)

        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        # 解析问题列表
        questions = []
        for line in content.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-")):
                # 移除编号和符号
                q = line.lstrip("0123456789.-.) ] ")
                if q:
                    questions.append(q)

        return questions if questions else [
            f"什么是 {topic}？",
            f"{topic} 的核心原理是什么？",
            f"{topic} 有哪些主要应用场景？",
            f"{topic} 的最新发展趋势是什么？",
            f"如何选择合适的 {topic} 方案？"
        ]

    def _get_system_prompt(self, depth: str) -> str:
        """获取系统提示词"""
        base = """你是一个专业的研究助手，擅长搜集、整理和分析信息。
你的任务是：
1. 搜索并收集准确、最新的信息
2. 分析信息的可靠性和相关性
3. 整理成清晰、结构化的回答
4. 引用可靠的信息来源

回答时请：
- 使用清晰的结构和标题
- 提供具体的数据和事实
- 标注信息来源
- 保持客观中立
"""

        depth_instructions = {
            "basic": "提供简洁的概述，重点突出核心信息。",
            "standard": "提供详细的说明，涵盖主要方面和细节。",
            "comprehensive": "提供全面深入的分析，包括背景、细节、对比、趋势等多个维度。"
        }

        return base + depth_instructions.get(depth, depth_instructions["standard"])

    def _format_user_query(self, query: SearchQuery) -> str:
        """格式化用户查询"""
        content = f"请帮我研究以下主题：{query.query}"

        if query.context:
            content += f"\n\n研究背景：{query.context}"

        content += f"\n\n请提供深度 {query.depth} 的研究结果。"

        return content

    def _parse_result(self, query: str, result: Dict) -> ResearchResult:
        """解析 API 结果"""
        if not result or "choices" not in result:
            return ResearchResult(
                topic=query,
                content="无法获取研究结果",
                sources=[]
            )

        choice = result["choices"][0]
        message = choice["message"]

        content = message.get("content", "")
        reasoning = message.get("reasoning_content", "")

        # 提取 token 使用情况
        usage = result.get("usage", {})

        return ResearchResult(
            topic=query,
            content=content,
            reasoning=reasoning,
            token_usage=usage
        )
