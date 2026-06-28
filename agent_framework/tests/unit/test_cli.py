"""
CLI 入口单元测试

测试 Click 命令行接口的行为
"""
import pytest
from click.testing import CliRunner
from pathlib import Path


class TestCLIInit:
    """CLI init 命令测试"""

    def test_init_command_creates_session_directory(self, tmp_path):
        """init命令创建会话目录"""
        from infrastructure.cli import cli

        runner = CliRunner()
        session_path = tmp_path / "test_session"

        result = runner.invoke(cli, [
            "init",
            "测试主题",
            "--session", str(session_path),
            "--workflow", "f1"
        ])

        # 验证命令成功
        assert result.exit_code == 0
        assert session_path.exists()
        assert session_path.is_dir()

    def test_init_command_creates_context_file(self, tmp_path):
        """init命令创建CONTEXT.md文件"""
        from infrastructure.cli import cli

        runner = CliRunner()
        session_path = tmp_path / "test_session"

        result = runner.invoke(cli, [
            "init",
            "测试主题",
            "--session", str(session_path)
        ])

        # 验证文件存在
        context_file = session_path / "CONTEXT.md"
        assert context_file.exists()
        content = context_file.read_text(encoding="utf-8")
        assert "测试主题" in content

    def test_init_command_creates_task_file(self, tmp_path):
        """init命令创建Task.md文件"""
        from infrastructure.cli import cli

        runner = CliRunner()
        session_path = tmp_path / "test_session"

        result = runner.invoke(cli, [
            "init",
            "测试主题",
            "--session", str(session_path)
        ])

        # 验证文件存在
        task_file = session_path / "Task.md"
        assert task_file.exists()
        content = task_file.read_text(encoding="utf-8")
        assert "测试主题" in content
        assert "Workflow:" in content

    def test_init_command_creates_readme_file(self, tmp_path):
        """init命令创建README.md文件"""
        from infrastructure.cli import cli

        runner = CliRunner()
        session_path = tmp_path / "test_session"

        result = runner.invoke(cli, [
            "init",
            "测试主题",
            "--session", str(session_path)
        ])

        # 验证文件存在
        readme_file = session_path / "README.md"
        assert readme_file.exists()


class TestCLIResume:
    """CLI resume 命令测试"""

    def test_resume_command_requires_existing_session(self, tmp_path):
        """resume命令需要已存在的会话目录"""
        from infrastructure.cli import cli

        runner = CliRunner()

        # 使用不存在的路径
        result = runner.invoke(cli, [
            "resume",
            "/non/existent/path"
        ])

        # 应该失败
        assert result.exit_code != 0

    def test_resume_command_accepts_existing_session(self, tmp_path):
        """resume命令接受已存在的会话目录"""
        from infrastructure.cli import cli

        # 先创建会话
        session_path = tmp_path / "test_session"
        session_path.mkdir()

        runner = CliRunner()
        result = runner.invoke(cli, [
            "resume",
            str(session_path)
        ])

        # 验证成功
        assert result.exit_code == 0
        assert "恢复会话" in result.output

    def test_resume_command_accepts_thread_id_option(self, tmp_path):
        """resume命令接受thread-id选项"""
        from infrastructure.cli import cli

        session_path = tmp_path / "test_session"
        session_path.mkdir()

        runner = CliRunner()
        result = runner.invoke(cli, [
            "resume",
            str(session_path),
            "--thread-id", "test-thread-123"
        ])

        assert result.exit_code == 0
        assert "test-thread-123" in result.output


class TestCLIRun:
    """CLI run 命令测试"""

    def test_run_command_accepts_valid_workflow_names(self):
        """run命令接受有效的workflow名称"""
        from infrastructure.cli import cli

        runner = CliRunner()

        for workflow in ["f1", "f2", "f3", "f4"]:
            result = runner.invoke(cli, [
                "run",
                workflow
            ])
            assert result.exit_code == 0
            assert workflow in result.output

    def test_run_command_rejects_invalid_workflow_name(self):
        """run命令拒绝无效的workflow名称"""
        from infrastructure.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, [
            "run",
            "invalid"
        ])

        # 应该失败（因为不在选项中）
        assert result.exit_code != 0


class TestCLIStatus:
    """CLI status 命令测试"""

    def test_status_command_displays_config(self):
        """status命令显示配置信息"""
        from infrastructure.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["status"])

        assert result.exit_code == 0
        assert "Agent Framework 状态" in result.output
        assert "LLM 配置" in result.output
        assert "Checkpoint 配置" in result.output
        assert "日志配置" in result.output


class TestCLIBase:
    """CLI 基础功能测试"""

    def test_cli_has_version_option(self):
        """CLI有version选项"""
        from infrastructure.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_cli_shows_help(self):
        """CLI显示帮助信息"""
        from infrastructure.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "ComindFlow Agent Framework CLI" in result.output
        assert "init" in result.output
        assert "resume" in result.output
        assert "run" in result.output
        assert "status" in result.output
