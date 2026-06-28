"""
CLI 入口模块

使用 Click 实现命令行接口
"""
import click
from pathlib import Path
from datetime import datetime
from typing import Optional


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """ComindFlow Agent Framework CLI"""
    pass


@cli.command()
@click.argument("topic")
@click.option("--session", "-s", help="会话目录路径")
@click.option("--workflow", "-w", default="f1", help="Workflow 名称 (f1, f2, f3, f4)")
def init(topic: str, session: str, workflow: str):
    """初始化新会话

    创建包含 CONTEXT.md 和 Task.md 的新会话目录
    """
    # 确定会话路径
    if not session:
        session = f"sessions/{topic.replace(' ', '_')}"

    session_path = Path(session)

    click.echo(f"初始化会话: {session_path}")
    click.echo(f"主题: {topic}")
    click.echo(f"Workflow: {workflow}")

    # 创建会话目录
    session_path.mkdir(parents=True, exist_ok=True)

    # 初始化文件
    (session_path / "CONTEXT.md").write_text(
        f"# {topic}\n\n"
        f"## 术语定义\n\n"
        f"## 关系\n\n"
        f"## 示例对话\n\n",
        encoding="utf-8"
    )

    (session_path / "Task.md").write_text(
        f"# {topic} - 学习任务\n\n"
        f"初始化时间: {datetime.now().isoformat()}\n"
        f"Workflow: {workflow}\n\n",
        encoding="utf-8"
    )

    (session_path / "README.md").write_text(
        f"# {topic}\n\n"
        f"初始化时间: {datetime.now().isoformat()}\n"
        f"Workflow: {workflow}\n\n"
        f"## 使用方法\n\n",
        encoding="utf-8"
    )

    click.echo(f"✓ 会话已创建: {session_path}")


@cli.command()
@click.argument("session_path", type=click.Path(exists=True))
@click.option("--thread-id", "-t", help="Checkpoint thread ID")
def resume(session_path: str, thread_id: str):
    """恢复会话

    从指定会话目录恢复之前的会话状态
    """
    click.echo(f"恢复会话: {session_path}")

    # 这里将来会连接 CheckpointManager
    click.echo(f"✓ 会话已恢复 (thread_id: {thread_id or 'default'})")


@cli.command()
@click.argument("workflow_name", type=click.Choice(["f1", "f2", "f3", "f4"]))
@click.option("--topic", "-t", help="研究/写作主题")
@click.option("--session", "-s", help="会话路径")
def run(workflow_name: str, topic: str, session: str):
    """运行指定 Workflow

    执行指定的工作流处理任务
    """
    click.echo(f"运行 Workflow: {workflow_name}")

    # 这里将来会加载并执行 workflow
    click.echo(f"✓ Workflow {workflow_name} 已启动")


@cli.command()
def status():
    """显示系统状态

    显示配置和系统信息
    """
    click.echo("=== Agent Framework 状态 ===\n")

    try:
        from config.settings import config
        click.echo(f"LLM 配置:")
        click.echo(f"  Model: {config.llm.model}")
        click.echo(f"  Base URL: {config.llm.base_url}")

        click.echo(f"\nCheckpoint 配置:")
        click.echo(f"  路径: {config.checkpoint.db_path}")
        click.echo(f"  清理周期: {config.checkpoint.cleanup_days} 天")

        click.echo(f"\n日志配置:")
        click.echo(f"  级别: {config.log.level}")
        click.echo(f"  文件: {config.log.file_path}")

        click.echo(f"\nAgent 配置:")
        click.echo(f"  确认级别: {config.confirmation_level}")
        click.echo(f"  最大重试: {config.max_retries}")
        click.echo(f"  超时: {config.timeout_seconds} 秒")
    except Exception as e:
        click.echo(f"配置加载失败: {e}")


if __name__ == "__main__":
    cli()
