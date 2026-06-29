"""
S3-T3: BudgetManager 单元测试

测试预算管理器的预算管理和驱逐策略功能。
"""

import pytest
from agent_framework.skills.budget_manager import BudgetManager


class TestBudgetManagerInitialization:
    """预算管理器初始化测试"""

    def test_initialization_with_default_values(self):
        """测试默认初始化"""
        budget = BudgetManager()

        assert budget.total_budget == 8000
        assert budget.metadata_reserve == 1000
        assert budget.available_budget == 7000  # 8000 - 1000

    def test_initialization_with_custom_values(self):
        """测试自定义初始化值"""
        budget = BudgetManager(total_budget=10000, metadata_reserve=2000)

        assert budget.total_budget == 10000
        assert budget.metadata_reserve == 2000
        assert budget.available_budget == 8000

    def test_can_load_with_sufficient_budget(self):
        """测试有足够预算时可以加载"""
        budget = BudgetManager(total_budget=8000, metadata_reserve=1000)

        # 可用预算 7000，加载 1000 token 应该可以
        assert budget.can_load("skill-1", 1000) is True

    def test_can_load_with_insufficient_budget(self):
        """测试预算不足时不可以加载"""
        budget = BudgetManager(total_budget=8000, metadata_reserve=1000)

        # 可用预算 7000，加载 8000 token 不应该可以
        assert budget.can_load("skill-1", 8000) is False

    def test_can_load_exactly_at_limit(self):
        """测试预算刚好等于可用预算时可以加载"""
        budget = BudgetManager(total_budget=8000, metadata_reserve=1000)

        # 可用预算 7000，加载 7000 token 应该可以
        assert budget.can_load("skill-1", 7000) is True


class TestBudgetManagerEviction:
    """驱逐策略测试"""

    def test_evict_if_needed_no_eviction_when_sufficient(self):
        """测试有足够预算时不驱逐"""
        budget = BudgetManager(total_budget=8000, metadata_reserve=1000)

        evicted = budget.evict_if_needed(1000)
        assert evicted == []

    def test_evict_if_needed_evicts_lru_skill(self):
        """测试驱逐最久未使用的技能"""
        budget = BudgetManager(total_budget=8000, metadata_reserve=1000)

        # 加载技能1（2000 tokens）
        budget.record_load("skill-1", 2000)
        # 加载技能2（3000 tokens）
        budget.record_load("skill-2", 3000)
        # 可用预算剩余 2000

        # 需要 4000 tokens，应该只驱逐技能1（释放 2000）
        evicted = budget.evict_if_needed(4000)
        assert "skill-1" in evicted
        assert "skill-2" not in evicted

    def test_evict_if_needed_multiple_skills(self):
        """测试驱逐多个技能以满足预算需求"""
        budget = BudgetManager(total_budget=8000, metadata_reserve=1000)

        # 加载多个技能
        budget.record_load("skill-1", 1500)
        budget.record_load("skill-2", 1500)
        budget.record_load("skill-3", 2000)
        # 可用预算剩余 2000

        # 需要 6000 tokens，应该驱逐技能1和技能2
        evicted = budget.evict_if_needed(6000)
        assert len(evicted) >= 2

    def test_lru_order_maintained(self):
        """测试 LRU 顺序正确维护"""
        budget = BudgetManager(total_budget=8000, metadata_reserve=1000)

        # 加载技能
        budget.record_load("skill-1", 1000)
        budget.record_load("skill-2", 1000)
        budget.record_load("skill-3", 1000)

        # 再次访问 skill-1，应该变成最近使用
        budget.record_load("skill-1", 1000)

        # 需要更多预算，驱逐时应该先驱逐 skill-2（最久未使用）
        evicted = budget.evict_if_needed(5000)
        assert "skill-2" in evicted
        assert "skill-3" in evicted
        assert "skill-1" not in evicted


class TestBudgetManagerStatus:
    """状态报告测试"""

    def test_get_status_returns_correct_info(self):
        """测试状态报告返回正确信息"""
        budget = BudgetManager(total_budget=8000, metadata_reserve=1000)

        status = budget.get_status()

        assert status["total_budget"] == 8000
        assert status["metadata_reserve"] == 1000
        assert status["available_budget"] == 7000
        assert status["loaded_skills_count"] == 0
        assert status["loaded_tokens"] == 0

    def test_get_status_after_loads(self):
        """测试加载技能后的状态报告"""
        budget = BudgetManager(total_budget=8000, metadata_reserve=1000)

        budget.record_load("skill-1", 2000)
        budget.record_load("skill-2", 1500)

        status = budget.get_status()

        assert status["loaded_skills_count"] == 2
        assert status["loaded_tokens"] == 3500
        assert status["available_budget"] == 3500
        assert status["utilization_percent"] == 43.75  # 3500/8000
