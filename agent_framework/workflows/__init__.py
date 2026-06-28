"""
Workflows 模块

包含所有业务流程定义。
"""

from agent_framework.workflows.f1_learning_research import create_f1_workflow
from agent_framework.workflows.f2_qa_enhanced import create_f2_workflow
from agent_framework.workflows.f3_academic_writing import create_f3_workflow
from agent_framework.workflows.f4_review_planning import create_f4_workflow

__all__ = [
    "create_f1_workflow",
    "create_f2_workflow",
    "create_f3_workflow",
    "create_f4_workflow"
]
