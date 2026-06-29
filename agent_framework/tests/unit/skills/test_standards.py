"""agent_framework.skills.standards 单元测试"""

import pytest

from agent_framework.skills.standards.instructions import (
    get_standard_instruction,
    StandardInstructionError,
)


class TestStandardInstructions:
    """标准化指令集单元测试"""

    def test_get_standard_instruction_returns_template(self):
        """测试获取标准化指令返回有效模板

        Given: 请求一个标准化指令模板
        When: 调用 get_standard_instruction
        Then: 返回包含必需指令元素的字符串
        """
        # Arrange & Act
        instruction = get_standard_instruction()

        # Assert
        assert isinstance(instruction, str)
        assert len(instruction) > 0
        # 应该包含标准的指令元素
        assert "Instructions for Claude" in instruction or "instructions" in instruction.lower()

    def test_get_instruction_with_skill_name(self):
        """测试带技能名称的指令

        Given: 指定一个技能名称
        When: 调用 get_standard_instruction(skill_name="grill-me")
        Then: 返回包含该技能名称的指令
        """
        # Arrange & Act
        instruction = get_standard_instruction(skill_name="grill-me")

        # Assert
        assert isinstance(instruction, str)
        assert "grill-me" in instruction.lower() or "grill" in instruction.lower()

    def test_get_instruction_with_custom_description(self):
        """测试带自定义描述的指令

        Given: 提供自定义描述
        When: 调用 get_standard_instruction(description="Custom skill")
        Then: 返回包含自定义描述的指令
        """
        # Arrange & Act
        instruction = get_standard_instruction(description="Test capability for testing")

        # Assert
        assert isinstance(instruction, str)
        assert "test capability" in instruction.lower()

    def test_invalid_skill_name_raises_error(self):
        """测试无效技能名称抛出错误

        Given: 提供无效的技能名称（如数字）
        When: 调用 get_standard_instruction(skill_name=123)
        Then: 抛出 StandardInstructionError
        """
        # Arrange & Act & Assert
        with pytest.raises(StandardInstructionError):
            get_standard_instruction(skill_name=123)

    def test_invalid_description_type_raises_error(self):
        """测试无效描述类型抛出错误

        Given: 提供无效的描述（如列表）
        When: 调用 get_standard_instruction(description=[])
        Then: 抛出 StandardInstructionError
        """
        # Arrange & Act & Assert
        with pytest.raises(StandardInstructionError):
            get_standard_instruction(description=[])


class TestStandardTools:
    """标准化工具接口单元测试"""

    def test_get_tool_interface_returns_template(self):
        """测试获取工具接口返回有效模板

        Given: 请求一个标准化工具接口
        When: 调用 get_tool_interface
        Then: 返回包含必需接口元素的字符串
        """
        # Arrange
        from agent_framework.skills.standards.tools import get_tool_interface

        # Act
        interface = get_tool_interface()

        # Assert
        assert isinstance(interface, str)
        assert len(interface) > 0
        assert "function" in interface.lower() or "def " in interface

    def test_get_tool_interface_with_name(self):
        """测试带工具名称的接口

        Given: 指定一个工具名称
        When: 调用 get_tool_interface(name="validate")
        Then: 返回包含该名称的接口
        """
        # Arrange
        from agent_framework.skills.standards.tools import get_tool_interface

        # Act
        interface = get_tool_interface(name="validate")

        # Assert
        assert isinstance(interface, str)
        assert "validate" in interface.lower()

    def test_get_tool_interface_with_parameters(self):
        """测试带参数的工具接口

        Given: 指定工具参数
        When: 调用 get_tool_interface(parameters={"input": "str"})
        Then: 返回包含参数定义的接口
        """
        # Arrange
        from agent_framework.skills.standards.tools import get_tool_interface

        # Act
        interface = get_tool_interface(parameters={"input": "str"})

        # Assert
        assert isinstance(interface, str)
        assert "input" in interface.lower()
