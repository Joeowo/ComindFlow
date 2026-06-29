"""
S3-T3: BudgetManager - 预算管理器

管理上下文 Token 预算，防止过度加载，支持 LRU 驱逐策略。
"""

from dataclasses import dataclass, field
from typing import Dict, List
from collections import OrderedDict
from loguru import logger


@dataclass
class BudgetManager:
    """预算管理器

    管理上下文 Token 预算，提供预算判断和 LRU 驱逐策略。

    Attributes:
        total_budget: 总预算，默认 8000 tokens
        metadata_reserve: 元数据保留预算，默认 1000 tokens
        available_budget: 可用预算（总预算 - 元数据保留）
        loaded_skills: 已加载技能及其大小，按 LRU 顺序存储
    """

    total_budget: int = 8000
    metadata_reserve: int = 1000
    available_budget: int = field(init=False)
    loaded_skills: Dict[str, int] = field(default_factory=OrderedDict)

    def __post_init__(self) -> None:
        """初始化后计算可用预算"""
        self.available_budget = self.total_budget - self.metadata_reserve
        logger.info(
            "BudgetManager initialized",
            total=self.total_budget,
            reserve=self.metadata_reserve,
            available=self.available_budget
        )

    def can_load(self, skill_name: str, estimated_tokens: int) -> bool:
        """判断是否可以加载技能

        Args:
            skill_name: 技能名称
            estimated_tokens: 预估需要消耗的 tokens

        Returns:
            是否有足够预算加载
        """
        if estimated_tokens <= 0:
            logger.warning("Invalid token estimate", skill=skill_name, tokens=estimated_tokens)
            return False

        can_load = estimated_tokens <= self.available_budget
        logger.debug(
            "Budget check",
            skill=skill_name,
            estimated=estimated_tokens,
            available=self.available_budget,
            can_load=can_load
        )
        return can_load

    def record_load(self, skill_name: str, actual_tokens: int) -> None:
        """记录技能加载

        Args:
            skill_name: 技能名称
            actual_tokens: 实际消耗的 tokens
        """
        self.loaded_skills[skill_name] = actual_tokens
        self.available_budget -= actual_tokens

        # 更新 LRU 顺序：将技能移到末尾（最近使用）
        self.loaded_skills.move_to_end(skill_name)

        logger.info(
            "Skill load recorded",
            skill=skill_name,
            tokens=actual_tokens,
            remaining=self.available_budget
        )

    def evict_if_needed(self, required_tokens: int) -> List[str]:
        """如果需要，驱逐技能以释放预算

        使用 LRU 策略驱逐最久未使用的技能。

        Args:
            required_tokens: 需要释放的 tokens 数量

        Returns:
            被驱逐的技能名称列表
        """
        if self.available_budget >= required_tokens:
            return []

        evicted = []
        tokens_to_free = required_tokens - self.available_budget

        # 按 LRU 顺序驱逐技能
        for skill_name, skill_tokens in list(self.loaded_skills.items()):
            if tokens_to_free <= 0:
                break

            evicted.append(skill_name)
            del self.loaded_skills[skill_name]
            self.available_budget += skill_tokens
            tokens_to_free -= skill_tokens

            logger.info(
                "Skill evicted",
                skill=skill_name,
                freed_tokens=skill_tokens,
                remaining_needed=tokens_to_free
            )

        if tokens_to_free > 0:
            logger.warning(
                "Insufficient budget even after eviction",
                still_needed=tokens_to_free
            )

        return evicted

    def get_status(self) -> Dict:
        """获取预算使用状态

        Returns:
            包含预算使用信息的字典
        """
        loaded_count = len(self.loaded_skills)
        loaded_tokens = sum(self.loaded_skills.values())

        return {
            "total_budget": self.total_budget,
            "metadata_reserve": self.metadata_reserve,
            "available_budget": self.available_budget,
            "loaded_skills_count": loaded_count,
            "loaded_tokens": loaded_tokens,
            "utilization_percent": (loaded_tokens / self.total_budget * 100) if self.total_budget > 0 else 0
        }
