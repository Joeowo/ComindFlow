"""标准化工具接口

提供 SKILL.md scripts/ 中工具脚本的标准接口格式。
"""


def get_tool_interface(
    name: str = "tool_name",
    description: str = "Description of what this tool does",
    parameters: dict | None = None,
    returns: str = "dict",
) -> str:
    """获取标准化工具接口模板

    Args:
        name: 工具函数名称
        description: 工具描述
        parameters: 参数字典，格式为 {"param_name": "param_type"}
        returns: 返回类型描述

    Returns:
        标准化的工具接口代码字符串
    """
    if parameters is None:
        parameters = {}

    # 生成参数列表
    param_list = []
    for param_name, param_type in parameters.items():
        param_list.append(f"    {param_name}: {param_type}")

    params_str = ",\n".join(param_list) if param_list else "    # No parameters"

    # 生成接口代码
    interface = f'''def {name}(
{params_str}
) -> {returns}:
    """{description}

    Returns:
        {returns}: {description.lower()}
    """
    # TODO: Implement the tool logic
    pass
'''

    return interface


def get_tool_class_template(
    class_name: str = "ToolHandler",
    description: str = "Handler for tool operations",
) -> str:
    """获取标准化工具类模板

    Args:
        class_name: 类名称
        description: 类描述

    Returns:
        标准化的工具类代码字符串
    """
    template = f'''class {class_name}:
    """{description}"""

    def __init__(self):
        """Initialize the tool handler."""
        self.name = "{class_name.lower()}"

    def execute(self, **kwargs) -> dict:
        """Execute the tool operation.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            dict: Operation result
        """
        # TODO: Implement the execute logic
        return {{"status": "success", "result": None}}
'''

    return template
