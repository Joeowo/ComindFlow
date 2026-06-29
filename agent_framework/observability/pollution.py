"""
S4-T6: 污染检测器

提供上下文污染检测功能。
"""

from typing import Dict, Any, Set

from agent_framework.observability.models.hallucination import (
    PollutionReport,
    UnauthorizedChange,
)


class ContextPollutionDetector:
    """上下文污染检测器

    检测未授权的状态修改和上下文污染。
    """

    def check_by_snapshot_comparison(
        self,
        before_state: Dict[str, Any],
        after_state: Dict[str, Any],
        whitelist: Set[str]
    ) -> PollutionReport:
        """通过状态快照对比检测污染

        Args:
            before_state: 变化前的状态
            after_state: 变化后的状态
            whitelist: 允许变更的键名集合

        Returns:
            PollutionReport: 污染检测报告
        """
        unauthorized_changes = []

        # 检查新增的键
        for key in after_state:
            if key not in before_state:
                # 新增的键，检查是否在白名单中
                if key not in whitelist:
                    unauthorized_changes.append(
                        UnauthorizedChange(
                            key=key,
                            old_value=None,
                            new_value=after_state[key]
                        )
                    )
            elif before_state[key] != after_state[key]:
                # 值发生变化，检查是否在白名单中
                if key not in whitelist:
                    unauthorized_changes.append(
                        UnauthorizedChange(
                            key=key,
                            old_value=before_state[key],
                            new_value=after_state[key]
                        )
                    )

        return PollutionReport(
            has_pollution=len(unauthorized_changes) > 0,
            unauthorized_changes=unauthorized_changes,
        )

    def check_by_whitelist(
        self,
        current_state: Dict[str, Any],
        whitelist: Set[str]
    ) -> PollutionReport:
        """通过白名单检测污染

        Args:
            current_state: 当前状态
            whitelist: 允许存在的键名集合

        Returns:
            PollutionReport: 污染检测报告
        """
        unauthorized_changes = []

        for key in current_state:
            if key not in whitelist:
                unauthorized_changes.append(
                    UnauthorizedChange(
                        key=key,
                        old_value=None,
                        new_value=current_state[key]
                    )
                )

        return PollutionReport(
            has_pollution=len(unauthorized_changes) > 0,
            unauthorized_changes=unauthorized_changes,
        )
