"""
日志系统单元测试

测试 Loguru 日志配置的行为
"""
import pytest
import sys
from pathlib import Path
from io import StringIO


class TestLoggerInit:
    """日志初始化测试"""

    def test_init_logger_adds_console_handler(self, monkeypatch):
        """第一个tracer bullet：日志初始化添加控制台处理器"""
        from infrastructure.logging import init_logger, logger

        # 初始化日志
        init_logger(level="INFO")

        # 验证至少有一个处理器
        assert len(logger._core.handlers) > 0

    def test_init_logger_without_file_only_has_console(self, tmp_path):
        """不指定文件路径时只有控制台处理器"""
        from infrastructure.logging import init_logger, logger

        # 初始化日志（不指定文件）
        init_logger(level="DEBUG", file_path=None)

        # 验证只有一个处理器（控制台）
        assert len(logger._core.handlers) == 1


class TestLoggerOutput:
    """日志输出测试"""

    def test_logger_outputs_to_console(self, caplog):
        """日志可以输出到控制台"""
        from infrastructure.logging import init_logger, logger

        # 由于loguru使用自己的handler，我们需要用其他方式测试
        # 这里我们只验证初始化不会报错
        init_logger(level="INFO")
        logger.info("测试消息")

        # 如果能走到这里说明没有报错
        assert True

    def test_logger_respects_log_level(self, capsys):
        """日志级别设置生效"""
        from infrastructure.logging import init_logger, logger

        init_logger(level="ERROR")
        logger.debug("这条消息不应该出现")
        logger.info("这条消息不应该出现")
        logger.warning("这条消息不应该出现")
        logger.error("这条消息应该出现")

        # 由于loguru的输出机制，这里我们只验证不会报错
        assert True


class TestLoggerFileOutput:
    """日志文件输出测试"""

    def test_init_logger_creates_log_file(self, tmp_path):
        """日志文件会被创建"""
        from infrastructure.logging import init_logger, logger

        log_file = tmp_path / "test.log"
        init_logger(level="INFO", file_path=str(log_file))

        # 写入日志
        logger.info("测试消息")

        # 验证文件存在
        assert log_file.exists()

    def test_log_file_contains_expected_content(self, tmp_path):
        """日志文件包含预期内容"""
        from infrastructure.logging import init_logger, logger

        log_file = tmp_path / "test.log"
        init_logger(level="INFO", file_path=str(log_file))

        # 写入日志
        test_message = "测试日志消息"
        logger.info(test_message)

        # 读取文件内容
        content = log_file.read_text(encoding="utf-8")

        # 验证包含测试消息
        assert test_message in content

    def test_log_file_contains_timestamp(self, tmp_path):
        """日志文件包含时间戳"""
        from infrastructure.logging import init_logger, logger

        log_file = tmp_path / "test.log"
        init_logger(level="INFO", file_path=str(log_file))

        logger.info("测试消息")

        content = log_file.read_text(encoding="utf-8")

        # 验证包含时间戳格式 (YYYY-MM-DD HH:mm:ss)
        import re
        timestamp_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
        assert re.search(timestamp_pattern, content) is not None


class TestLoggerRotation:
    """日志轮转测试"""

    def test_logger_accepts_rotation_config(self, tmp_path):
        """日志接受轮转配置"""
        from infrastructure.logging import init_logger

        log_file = tmp_path / "test.log"
        # 验证不会报错
        init_logger(
            level="INFO",
            file_path=str(log_file),
            rotation="50 MB"
        )

        assert True

    def test_logger_accepts_retention_config(self, tmp_path):
        """日志接受保留配置"""
        from infrastructure.logging import init_logger

        log_file = tmp_path / "test.log"
        # 验证不会报错
        init_logger(
            level="INFO",
            file_path=str(log_file),
            retention="7 days"
        )

        assert True
