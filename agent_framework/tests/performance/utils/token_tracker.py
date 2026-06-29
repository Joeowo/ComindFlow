"""
Token 使用量跟踪工具

从 DeepSeek API 响应中提取真实的 token 使用数据，
用于性能测试和消融实验。
"""
import os
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TokenUsage:
    """Token 使用量数据"""
    prompt_tokens: int = 0          # 输入 tokens
    completion_tokens: int = 0     # 输出 tokens
    total_tokens: int = 0           # 总 tokens
    reasoning_tokens: int = 0       # 推理 tokens (如果有的话)
    cached: bool = False            # 是否来自缓存

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "cached": self.cached
        }

    @classmethod
    def from_response(cls, response: Dict) -> 'TokenUsage':
        """从 API 响应创建 TokenUsage"""
        usage = response.get("usage", {})

        return cls(
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            reasoning_tokens=usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0),
            cached=False
        )

    @classmethod
    def estimate(cls, text: str) -> 'TokenUsage':
        """估算 Token 使用量（用于无 API 调用时）"""
        estimated = len(text) // 4
        return cls(
            prompt_tokens=estimated,
            completion_tokens=0,
            total_tokens=estimated,
            reasoning_tokens=0,
            cached=True
        )


class TokenTracker:
    """Token 使用量跟踪器"""

    def __init__(self):
        self._history: list[TokenUsage] = []

    def record(self, usage: TokenUsage, operation: str = "") -> None:
        """记录 Token 使用"""
        if operation:
            usage.operation = operation
        self._history.append(usage)

    def get_total_tokens(self) -> int:
        """获取累计总 Token 数"""
        return sum(u.total_tokens for u in self._history)

    def get_average_tokens(self) -> float:
        """获取平均 Token 数"""
        if not self._history:
            return 0.0
        return self.get_total_tokens() / len(self._history)

    def get_latest(self) -> Optional[TokenUsage]:
        """获取最新的 Token 记录"""
        return self._history[-1] if self._history else None

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self._history:
            return {"count": 0, "total_tokens": 0}

        total = self.get_total_tokens()
        cached_count = sum(1 for u in self._history if u.cached)
        real_count = len(self._history) - cached_count

        return {
            "count": len(self._history),
            "total_tokens": total,
            "cached_count": cached_count,
            "real_api_calls": real_count,
            "average_tokens": self.get_average_tokens(),
            "prompt_tokens_total": sum(u.prompt_tokens for u in self._history),
            "completion_tokens_total": sum(u.completion_tokens for u in self._history)
        }

    def clear(self) -> None:
        """清空历史记录"""
        self._history.clear()

    def get_history(self) -> list[TokenUsage]:
        """获取历史记录"""
        return self._history.copy()


# 全局跟踪器实例
_global_tracker: Optional[TokenTracker] = None


def get_token_tracker() -> TokenTracker:
    """获取全局 Token 跟踪器"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = TokenTracker()
    return _global_tracker


def record_api_usage(response: Dict, operation: str = "") -> None:
    """记录 API 调用的 Token 使用"""
    tracker = get_token_tracker()
    usage = TokenUsage.from_response(response)
    tracker.record(usage, operation)


def record_estimated_usage(text: str, operation: str = "") -> None:
    """记录估算的 Token 使用（用于缓存或无 API 调用时）"""
    tracker = get_token_tracker()
    usage = TokenUsage.estimate(text)
    tracker.record(usage, operation)


def get_usage_stats() -> Dict[str, Any]:
    """获取当前 Token 统计"""
    tracker = get_token_tracker()
    return tracker.get_stats()


# 从环境变量加载 API 配置
def load_api_config() -> Dict[str, str]:
    """从 .env 文件加载 API 配置"""
    env_path = Path("AutoResearch/.env")
    if not env_path.exists():
        return {}

    config = {}
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()

    return config
