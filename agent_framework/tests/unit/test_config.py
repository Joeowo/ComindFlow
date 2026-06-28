"""
配置管理模块单元测试

测试 Pydantic 配置系统的行为
"""
import os
import pytest
from pathlib import Path


class TestLLMConfig:
    """LLMConfig 测试"""

    def test_can_load_llm_config_from_env(self, monkeypatch):
        """第一个tracer bullet：配置可以从环境变量加载"""
        # Arrange: 设置环境变量
        monkeypatch.setenv("LLM_API_KEY", "test_key_123")
        monkeypatch.setenv("LLM_BASE_URL", "https://api.test.com/v1")
        monkeypatch.setenv("LLM_MODEL", "gpt-4-test")

        # Act: 导入并创建配置
        from config.settings import LLMConfig
        config = LLMConfig()

        # Assert: 验证值正确加载
        assert config.api_key == "test_key_123"
        assert config.base_url == "https://api.test.com/v1"
        assert config.model == "gpt-4-test"


class TestCheckpointConfig:
    """CheckpointConfig 测试"""

    def test_can_load_checkpoint_config_from_env(self, monkeypatch):
        """配置可以从环境变量加载"""
        monkeypatch.setenv("CHECKPOINT_DB_PATH", "/tmp/test.db")
        monkeypatch.setenv("CHECKPOINT_CLEANUP_DAYS", "7")

        from config.settings import CheckpointConfig
        config = CheckpointConfig()

        assert config.db_path == "/tmp/test.db"
        assert config.cleanup_days == 7


class TestLogConfig:
    """LogConfig 测试"""

    def test_can_load_log_config_from_env(self, monkeypatch):
        """配置可以从环境变量加载"""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("LOG_FILE_PATH", "/tmp/test.log")
        monkeypatch.setenv("LOG_ROTATION", "50 MB")
        monkeypatch.setenv("LOG_RETENTION", "7 days")

        from config.settings import LogConfig
        config = LogConfig()

        assert config.level == "DEBUG"
        assert config.file_path == "/tmp/test.log"
        assert config.rotation == "50 MB"
        assert config.retention == "7 days"


class TestConfigDefaults:
    """默认值测试"""

    def test_llm_config_has_sensible_defaults(self, monkeypatch):
        """LLMConfig有合理的默认值"""
        monkeypatch.setenv("LLM_API_KEY", "test_key")

        from config.settings import LLMConfig
        config = LLMConfig()

        assert config.base_url == "https://api.openai.com/v1"
        assert config.model == "gpt-4"
        assert config.temperature == 0.7
        assert config.max_tokens == 2000

    def test_checkpoint_config_has_sensible_defaults(self):
        """CheckpointConfig有合理的默认值"""
        from config.settings import CheckpointConfig
        config = CheckpointConfig()

        assert config.db_path == "agent_framework/checkpoints.db"
        assert config.cleanup_days == 30

    def test_log_config_has_sensible_defaults(self):
        """LogConfig有合理的默认值"""
        from config.settings import LogConfig
        config = LogConfig()

        assert config.level == "INFO"
        assert config.file_path == "agent_framework/logs/agent.log"
        assert config.rotation == "100 MB"
        assert config.retention == "30 days"


class TestAgentConfig:
    """AgentConfig 总配置测试"""

    def test_agent_config_loads_nested_configs(self, monkeypatch):
        """AgentConfig可以加载嵌套配置"""
        monkeypatch.setenv("LLM_API_KEY", "test_key")
        monkeypatch.setenv("CHECKPOINT_DB_PATH", "/tmp/checkpoints.db")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        from config.settings import AgentConfig
        config = AgentConfig()

        # 验证嵌套配置正确加载
        assert config.llm.api_key == "test_key"
        assert config.checkpoint.db_path == "/tmp/checkpoints.db"
        assert config.log.level == "DEBUG"

    def test_agent_config_has_sensible_defaults(self):
        """AgentConfig有合理的默认值"""
        from config.settings import AgentConfig
        config = AgentConfig()

        assert config.confirmation_level == "balanced"
        assert config.max_retries == 3
        assert config.timeout_seconds == 60


class TestConfigValidation:
    """类型验证测试"""

    def test_llm_config_validates_temperature_range(self, monkeypatch):
        """LLMConfig验证temperature在有效范围"""
        monkeypatch.setenv("LLM_API_KEY", "test_key")

        from config.settings import LLMConfig
        from pydantic import ValidationError

        # 有效值
        config = LLMConfig(temperature=0.5)
        assert config.temperature == 0.5

        # 边界值
        config = LLMConfig(temperature=2.0)
        assert config.temperature == 2.0

        # 超出范围应该报错
        with pytest.raises(ValidationError):
            LLMConfig(temperature=2.1)

        with pytest.raises(ValidationError):
            LLMConfig(temperature=-0.1)

    def test_checkpoint_config_validates_cleanup_days_positive(self, monkeypatch):
        """CheckpointConfig验证cleanup_days为正数"""
        from config.settings import CheckpointConfig
        from pydantic import ValidationError

        # 有效值
        config = CheckpointConfig(cleanup_days=7)
        assert config.cleanup_days == 7

        # 无效值应该报错
        with pytest.raises(ValidationError):
            CheckpointConfig(cleanup_days=0)

        with pytest.raises(ValidationError):
            CheckpointConfig(cleanup_days=-5)

    def test_agent_config_validates_confirmation_level(self):
        """AgentConfig验证confirmation_level的值"""
        from config.settings import AgentConfig
        from pydantic import ValidationError

        # 有效值
        for level in ["minimal", "balanced", "thorough"]:
            config = AgentConfig(confirmation_level=level)
            assert config.confirmation_level == level

        # 无效值应该报错
        with pytest.raises(ValidationError):
            AgentConfig(confirmation_level="invalid")

    def test_agent_config_validates_max_retries_positive(self):
        """AgentConfig验证max_retries为正数"""
        from config.settings import AgentConfig
        from pydantic import ValidationError

        # 有效值
        config = AgentConfig(max_retries=5)
        assert config.max_retries == 5

        # 无效值应该报错
        with pytest.raises(ValidationError):
            AgentConfig(max_retries=0)

        with pytest.raises(ValidationError):
            AgentConfig(max_retries=-1)
