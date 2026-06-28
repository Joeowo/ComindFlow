"""
Workflows 模块

包含所有业务流程定义。
"""

from agent_framework.workflows.f1_learning_research import create_f1_workflow
from agent_framework.workflows.f2_qa_enhanced import create_f2_workflow

__all__ = ["create_f1_workflow", "create_f2_workflow"]
