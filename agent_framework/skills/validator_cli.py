"""SKILL.md 验证工具 CLI

提供命令行接口验证 SKILL.md 文件规范。
"""

import argparse
import sys
from pathlib import Path

from agent_framework.skills.validator import SkillValidator


def main() -> int:
    """CLI 主入口

    Returns:
        退出代码（0=成功，1=失败）
    """
    parser = argparse.ArgumentParser(description="验证 SKILL.md 规范")
    parser.add_argument("path", help="SKILL.md 文件路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()
    skill_path = Path(args.path)

    validator = SkillValidator()
    result = validator.validate(skill_path)

    # 输出结果
    if result.valid:
        print(f"✅ {skill_path}: 验证通过")
    else:
        print(f"❌ {skill_path}: 验证失败")

    # 输出错误
    for error in result.errors:
        print(f"  ❌ 错误: {error}")

    # 输出警告
    for warning in result.warnings:
        print(f"  ⚠️  警告: {warning}")

    if args.verbose and result.valid:
        print(f"\n详细信息:")
        print(f"  - 文件: {skill_path}")
        print(f"  - 状态: 有效")
        print(f"  - 警告数: {len(result.warnings)}")

    return 0 if result.valid else 1


if __name__ == "__main__":
    sys.exit(main())
