"""技能生命周期管理 CLI

提供命令行接口管理技能生命周期。
"""

import argparse
import sys
from pathlib import Path

from agent_framework.skills.lifecycle import SkillLifecycle


def cmd_discover(args) -> int:
    """发现技能命令"""
    lifecycle = SkillLifecycle()
    skills_dir = Path(args.path)

    skills = lifecycle.discover(skills_dir)

    print(f"在 {skills_dir} 中发现 {len(skills)} 个技能:")
    for skill in skills:
        print(f"  - {skill.name} ({skill.path})")

    return 0


def cmd_health(args) -> int:
    """健康检查命令"""
    lifecycle = SkillLifecycle()
    skills_dir = Path(args.path)

    # 发现技能
    skills = lifecycle.discover(skills_dir)
    if not skills:
        print(f"在 {skills_dir} 中没有发现技能")
        return 1

    # 注册并检查健康状态
    all_healthy = True
    for skill in skills:
        lifecycle.register(skill)
        health = lifecycle.get_health(skill.name)

        if health and health.healthy:
            print(f"✅ {skill.name}: 健康")
        else:
            print(f"❌ {skill.name}: 不健康 - {health.message if health else '未知'}")
            all_healthy = False

    return 0 if all_healthy else 1


def cmd_stats(args) -> int:
    """统计信息命令"""
    lifecycle = SkillLifecycle()
    skills_dir = Path(args.path)

    # 发现并注册技能
    skills = lifecycle.discover(skills_dir)
    for skill in skills:
        lifecycle.register(skill)

    print(f"技能统计 ({skills_dir}):")
    print(f"  - 总技能数: {len(skills)}")

    for skill in skills:
        stats = lifecycle.get_stats(skill.name)
        if stats:
            print(f"\n  {skill.name}:")
            print(f"    - 版本: {stats['version']}")
            print(f"    - 状态: {'已加载' if stats['loaded'] else '未加载'}")
            print(f"    - 执行次数: {stats['execution_count']}")

    return 0


def main() -> int:
    """CLI 主入口

    Returns:
        退出代码（0=成功，1=失败）
    """
    parser = argparse.ArgumentParser(description="技能生命周期管理")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # discover 命令
    discover_parser = subparsers.add_parser("discover", help="发现技能")
    discover_parser.add_argument("path", help="技能目录路径")

    # health 命令
    health_parser = subparsers.add_parser("health", help="健康检查")
    health_parser.add_argument("path", help="技能目录路径")

    # stats 命令
    stats_parser = subparsers.add_parser("stats", help="统计信息")
    stats_parser.add_argument("path", help="技能目录路径")

    args = parser.parse_args()

    if args.command == "discover":
        return cmd_discover(args)
    elif args.command == "health":
        return cmd_health(args)
    elif args.command == "stats":
        return cmd_stats(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
