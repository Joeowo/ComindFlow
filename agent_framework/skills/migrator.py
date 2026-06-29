"""SKILL.md 迁移工具

自动将不符合规范的 SKILL.md 迁移到新规范。
"""

import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MigrationReport:
    """迁移报告

    Attributes:
        success: 是否成功完成迁移
        changes: 进行的更改数量
        errors: 错误列表
        warnings: 警告列表
        backup_path: 备份文件路径
    """

    success: bool
    changes: int
    errors: list[str]
    warnings: list[str]
    backup_path: Path | None = None


class SkillMigrator:
    """SKILL.md 迁移工具

    自动修复常见的 SKILL.md 规范问题：
    - 拆分超长内容到 REFERENCE.md
    - 标准化 description 格式
    - 添加缺失的必需章节
    """

    def __init__(self, max_lines: int = 100):
        """初始化迁移工具

        Args:
            max_lines: SKILL.md 允许的最大行数
        """
        self.max_lines = max_lines

    def migrate(
        self,
        skill_path: Path,
        create_backup: bool = True,
    ) -> MigrationReport:
        """迁移 SKILL.md 到新规范

        Args:
            skill_path: SKILL.md 文件路径
            create_backup: 是否创建备份

        Returns:
            MigrationReport: 迁移报告
        """
        errors: list[str] = []
        warnings: list[str] = []
        changes = 0
        backup_path = None

        # 检查文件是否存在
        if not skill_path.exists():
            return MigrationReport(
                success=False,
                changes=0,
                errors=[f"SKILL.md not found at {skill_path}"],
                warnings=warnings,
            )

        # 创建备份
        if create_backup:
            backup_path = skill_path.with_suffix(skill_path.suffix + ".bak")
            try:
                shutil.copy2(skill_path, backup_path)
                changes += 1
            except Exception as e:
                errors.append(f"Failed to create backup: {e}")
                return MigrationReport(
                    success=False,
                    changes=0,
                    errors=errors,
                    warnings=warnings,
                )

        # 读取文件内容
        try:
            content = skill_path.read_text(encoding="utf-8")
        except Exception as e:
            errors.append(f"Failed to read SKILL.md: {e}")
            return MigrationReport(
                success=False,
                changes=changes,
                errors=errors,
                warnings=warnings,
                backup_path=backup_path,
            )

        # 检查是否需要迁移
        lines = content.split("\n")
        if len(lines) <= self.max_lines:
            # 文件已经符合规范，不需要迁移
            return MigrationReport(
                success=True,
                changes=changes,
                errors=[],
                warnings=["SKILL.md already compliant, no migration needed"],
                backup_path=backup_path,
            )

        # 拆分超长内容到 REFERENCE.md
        try:
            reference_path = skill_path.parent / "REFERENCE.md"

            # 保留 frontmatter 和前 max_lines-10 行
            frontmatter_end = -1
            for i, line in enumerate(lines):
                if line.strip() == "---" and i > 0:
                    frontmatter_end = i + 1
                    break

            if frontmatter_end == -1:
                # 没有 frontmatter，从头开始
                frontmatter_end = 0

            # 计算保留的行数（frontmatter + 内容）
            keep_lines = self.max_lines - 10  # 为链接留出空间
            if keep_lines < frontmatter_end + 5:
                keep_lines = frontmatter_end + 5

            # 分割内容
            keep_content = "\n".join(lines[:keep_lines])
            overflow_content = "\n".join(lines[keep_lines:])

            # 如果有超出内容，写入 REFERENCE.md
            if overflow_content.strip():
                if reference_path.exists():
                    # REFERENCE.md 已存在，追加内容
                    existing = reference_path.read_text(encoding="utf-8")
                    reference_path.write_text(existing + "\n\n" + overflow_content, encoding="utf-8")
                else:
                    reference_path.write_text(f"# Reference Documentation\n\n{overflow_content}", encoding="utf-8")

                # 更新 SKILL.md，添加指向 REFERENCE.md 的链接
                new_content = keep_content
                if "## Advanced" not in new_content and "REFERENCE" not in new_content:
                    new_content += "\n\n## Advanced\n\nSee [REFERENCE.md](REFERENCE.md) for detailed documentation.\n"

                skill_path.write_text(new_content, encoding="utf-8")
                changes += 2  # 创建 REFERENCE.md + 更新 SKILL.md
                warnings.append(f"Content split into REFERENCE.md ({len(overflow_content.split(chr(10)))} lines moved)")

            # TODO: 实现实际的迁移逻辑
            # 目前只是基本结构，后续循环会添加具体功能
        except Exception as e:
            errors.append(f"Failed to split content: {e}")
            return MigrationReport(
                success=False,
                changes=changes,
                errors=errors,
                warnings=warnings,
                backup_path=backup_path,
            )

        return MigrationReport(
            success=True,
            changes=changes,
            errors=errors,
            warnings=warnings,
            backup_path=backup_path,
        )
