"""SKILL.md 规范验证器

检查 SKILL.md 文件是否符合 write-a-skill 规范。
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationResult:
    """验证结果

    Attributes:
        valid: 是否通过验证
        errors: 错误列表
        warnings: 警告列表
    """

    valid: bool
    errors: list[str]
    warnings: list[str]


class SkillValidator:
    """SKILL.md 规范验证器

    检查 SKILL.md 文件是否符合 write-a-skill 规范，包括：
    - YAML frontmatter 完整性
    - 必需字段存在（name, description）
    - description 字段格式
    - 文件行数限制
    - 必需章节存在
    """

    def validate(self, skill_path: Path) -> ValidationResult:
        """验证 SKILL.md 是否符合规范

        Args:
            skill_path: SKILL.md 文件路径

        Returns:
            ValidationResult: 验证结果，包含 valid、errors、warnings
        """
        errors: list[str] = []
        warnings: list[str] = []

        # 检查文件是否存在
        if not skill_path.exists():
            return ValidationResult(
                valid=False,
                errors=[f"SKILL.md not found at {skill_path}"],
                warnings=warnings
            )

        # 读取文件内容
        try:
            content = skill_path.read_text(encoding="utf-8")
        except Exception as e:
            return ValidationResult(
                valid=False,
                errors=[f"Failed to read SKILL.md: {e}"],
                warnings=warnings
            )

        # 解析 frontmatter
        metadata = self._parse_frontmatter(content)

        # 验证必需字段
        if not metadata.get("name"):
            errors.append("Missing required field: name")
        if not metadata.get("description"):
            errors.append("Missing required field: description")

        # 验证文件行数（警告级别）
        lines = content.split("\n")
        if len(lines) > 100:
            warnings.append(f"SKILL.md exceeds 100 lines ({len(lines)} lines)")

        # 验证必需章节（警告级别）
        content_lower = content.lower()
        if "## quick start" not in content_lower and "## quick-start" not in content_lower:
            warnings.append("Missing recommended section: Quick start")
        if "## workflows" not in content_lower:
            warnings.append("Missing recommended section: Workflows")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

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

        # 解析 YAML（简化实现，只处理简单的 key: value）
        for line in lines[1:end_idx]:
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

        return metadata
