"""SKILL.md 迁移工具 CLI

提供命令行接口迁移 SKILL.md 文件到新规范。
"""

import argparse
import sys
from pathlib import Path

from agent_framework.skills.migrator import SkillMigrator


def main() -> int:
    """CLI 主入口

    Returns:
        退出代码（0=成功，1=失败）
    """
    parser = argparse.ArgumentParser(description="迁移 SKILL.md 到新规范")
    parser.add_argument("path", help="SKILL.md 文件路径")
    parser.add_argument("--max-lines", type=int, default=100, help="最大行数限制")
    parser.add_argument("--no-backup", action="store_true", help="不创建备份")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()
    skill_path = Path(args.path)

    migrator = SkillMigrator(max_lines=args.max_lines)
    report = migrator.migrate(skill_path, create_backup=not args.no_backup)

    # 输出结果
    if report.success:
        print(f"✅ {skill_path}: 迁移成功")
    else:
        print(f"❌ {skill_path}: 迁移失败")

    # 输出错误
    for error in report.errors:
        print(f"  ❌ 错误: {error}")

    # 输出警告
    for warning in report.warnings:
        print(f"  ⚠️  警告: {warning}")

    if args.verbose:
        print(f"\n详细信息:")
        print(f"  - 文件: {skill_path}")
        print(f"  - 更改数: {report.changes}")
        print(f"  - 备份: {report.backup_path}")

    return 0 if report.success else 1


if __name__ == "__main__":
    sys.exit(main())
