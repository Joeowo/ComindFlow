"""技能生命周期管理

管理技能的注册、加载、卸载和监控。
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class SkillRegistration:
    """技能注册记录

    Attributes:
        name: 技能名称
        path: 技能目录路径
        version: 技能版本
        active: 是否激活
        registered_at: 注册时间
    """

    name: str
    path: Path
    version: str = "1.0"
    active: bool = True
    registered_at: datetime | None = None

    def __post_init__(self):
        """初始化后处理"""
        if self.registered_at is None:
            self.registered_at = datetime.now()


@dataclass
class SkillHealthStatus:
    """技能健康状态

    Attributes:
        healthy: 是否健康
        message: 状态消息
        last_check: 检查时间
    """

    healthy: bool
    message: str
    last_check: datetime = field(default_factory=datetime.now)


class SkillLifecycle:
    """技能生命周期管理器

    管理技能的注册、注销、加载和卸载。
    """

    def __init__(self):
        """初始化生命周期管理器"""
        self._registrations: dict[str, SkillRegistration] = {}
        self._loaded: set[str] = set()
        self._execution_counts: dict[str, int] = {}

    def discover(self, skills_dir: Path) -> list[SkillRegistration]:
        """扫描目录发现技能

        Args:
            skills_dir: 技能目录路径

        Returns:
            发现的技能注册记录列表
        """
        registrations: list[SkillRegistration] = []

        if not skills_dir.exists() or not skills_dir.is_dir():
            return registrations

        # 扫描子目录中的 SKILL.md 文件
        for skill_path in skills_dir.iterdir():
            if skill_path.is_dir():
                skill_md = skill_path / "SKILL.md"
                if skill_md.exists():
                    # 解析 frontmatter 获取技能名称
                    try:
                        content = skill_md.read_text(encoding="utf-8")
                        metadata = self._parse_frontmatter(content)
                        name = metadata.get("name", skill_path.name)

                        registration = SkillRegistration(
                            name=name,
                            path=skill_path,
                            version=metadata.get("version", "1.0"),
                        )
                        registrations.append(registration)
                    except Exception:
                        # 跳过无法读取的技能
                        continue

        return registrations

    def _parse_frontmatter(self, content: str) -> dict:
        """解析 YAML frontmatter

        Args:
            content: 文件内容

        Returns:
            解析后的元数据字典
        """
        metadata: dict = {}
        lines = content.split("\n")

        if not lines or lines[0] != "---":
            return metadata

        # 找到结束的 ---
        end_idx = -1
        for i, line in enumerate(lines[1:], start=1):
            if line == "---":
                end_idx = i
                break

        if end_idx == -1:
            return metadata

        # 解析 YAML（简化实现）
        for line in lines[1:end_idx]:
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

        return metadata

    def register(self, registration: SkillRegistration) -> None:
        """注册技能

        Args:
            registration: 技能注册记录

        Raises:
            ValueError: 当技能已注册时
        """
        if registration.name in self._registrations:
            raise ValueError(f"Skill '{registration.name}' is already registered")

        self._registrations[registration.name] = registration

    def unregister(self, skill_name: str) -> None:
        """注销技能

        Args:
            skill_name: 技能名称

        Note:
            如果技能不存在，静默忽略
        """
        self._registrations.pop(skill_name, None)

    def is_registered(self, skill_name: str) -> bool:
        """检查技能是否已注册

        Args:
            skill_name: 技能名称

        Returns:
            是否已注册
        """
        return skill_name in self._registrations

    def list_registered(self) -> list[str]:
        """列出所有已注册的技能名称

        Returns:
            技能名称列表
        """
        return list(self._registrations.keys())

    def get_registration(self, skill_name: str) -> SkillRegistration | None:
        """获取技能注册记录

        Args:
            skill_name: 技能名称

        Returns:
            技能注册记录，如果不存在返回 None
        """
        return self._registrations.get(skill_name)

    def load(self, skill_name: str) -> str | None:
        """加载技能内容

        Args:
            skill_name: 技能名称

        Returns:
            SKILL.md 内容，如果技能不存在返回 None
        """
        registration = self._registrations.get(skill_name)
        if registration is None:
            return None

        skill_md = registration.path / "SKILL.md"
        if not skill_md.exists():
            return None

        try:
            content = skill_md.read_text(encoding="utf-8")
            self._loaded.add(skill_name)
            return content
        except Exception:
            return None

    def unload(self, skill_name: str) -> None:
        """卸载技能

        Args:
            skill_name: 技能名称

        Note:
            如果技能不存在，静默忽略
        """
        self._loaded.discard(skill_name)

    def is_loaded(self, skill_name: str) -> bool:
        """检查技能是否已加载

        Args:
            skill_name: 技能名称

        Returns:
            是否已加载
        """
        return skill_name in self._loaded

    def list_loaded(self) -> list[str]:
        """列出所有已加载的技能名称

        Returns:
            已加载技能名称列表
        """
        return list(self._loaded)

    def get_stats(self, skill_name: str) -> dict | None:
        """获取技能统计信息

        Args:
            skill_name: 技能名称

        Returns:
            统计信息字典，如果技能不存在返回 None
        """
        registration = self._registrations.get(skill_name)
        if registration is None:
            return None

        return {
            "name": registration.name,
            "version": registration.version,
            "active": registration.active,
            "loaded": skill_name in self._loaded,
            "registered_at": registration.registered_at.isoformat(),
            "execution_count": self._execution_counts.get(skill_name, 0),
        }

    def get_health(self, skill_name: str) -> SkillHealthStatus | None:
        """获取技能健康状态

        Args:
            skill_name: 技能名称

        Returns:
            健康状态，如果技能不存在返回 None
        """
        registration = self._registrations.get(skill_name)
        if registration is None:
            return None

        # 检查 SKILL.md 是否存在
        skill_md = registration.path / "SKILL.md"
        if not skill_md.exists():
            return SkillHealthStatus(
                healthy=False,
                message=f"SKILL.md not found at {skill_md}",
            )

        # 检查是否可读
        try:
            skill_md.read_text(encoding="utf-8")
        except Exception as e:
            return SkillHealthStatus(
                healthy=False,
                message=f"Failed to read SKILL.md: {e}",
            )

        return SkillHealthStatus(
            healthy=True,
            message="Skill is healthy",
        )

    def record_execution(self, skill_name: str) -> None:
        """记录技能执行

        Args:
            skill_name: 技能名称

        Note:
            如果技能不存在，静默忽略
        """
        if skill_name in self._registrations:
            self._execution_counts[skill_name] = self._execution_counts.get(skill_name, 0) + 1
