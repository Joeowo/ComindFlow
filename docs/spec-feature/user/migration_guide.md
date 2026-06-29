# Agent Framework 技能系统 - 迁移指南

本文档帮助您将现有的技能迁移到新的规范格式。

---

## 迁移概览

新规范对 `SKILL.md` 文件格式进行了标准化，主要变化：

1. **必须的 YAML frontmatter**：包含技能元数据
2. **标准化的字段**：`name`, `description`, `version`, `category`, `tags`
3. **内容分离**：超长内容可拆分到 `REFERENCE.md`

---

## 准备工作

### 1. 备份现有技能

```bash
# 备份整个 skills 目录
cp -r skills/ skills-backup/

# 或使用 git
git add skills/
git commit -m "Backup before migration"
```

### 2. 检查当前格式

查看现有技能文件是否符合新规范：

```bash
python -m agent_framework.skills.validator_cli validate-all
```

---

## 迁移步骤

### 步骤 1: 添加 YAML frontmatter

每个技能文件必须以 YAML frontmatter 开头：

```markdown
---
name: skill-name
description: Brief description of the skill
version: 1.0
category: general
tags: [keyword1, keyword2]
---

# Skill Name

Skill content here...
```

### 步骤 2: 验证字段

确保所有必须字段存在：

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | ✅ | 技能名称，必须唯一 |
| `description` | ✅ | 技能描述 |
| `version` | ❌ | 版本号，默认 "1.0" |
| `category` | ❌ | 分类，用于路由 |
| `tags` | ❌ | 标签列表，便于发现 |

### 步骤 3: 处理超长内容

如果技能内容超过 200 行，考虑拆分：

```bash
# 使用迁移工具自动拆分
python -m agent_framework.skills.migrator_cli migrate skills/my-skill/
```

这会创建：
- `SKILL.md`：包含 frontmatter 和主要说明
- `REFERENCE.md`：包含详细参考内容

### 步骤 4: 验证迁移结果

```bash
# 验证单个技能
python -m agent_framework.skills.validator_cli validate skills/my-skill/

# 验证所有技能
python -m agent_framework.skills.validator_cli validate-all
```

---

## 自动化迁移

### 使用 CLI 工具

#### 迁移单个技能

```bash
python -m agent_framework.skills.migrator_cli migrate skills/my-skill/
```

#### 迁移所有技能

```bash
python -m agent_framework.skills.migrator_cli migrate-all
```

#### 迁移选项

```bash
# 干运行（不修改文件）
python -m agent_framework.skills.migrator_cli migrate skills/my-skill/ --dry-run

# 保留原文件
python -m agent_framework.skills.migrator_cli migrate skills/my-skill/ --backup
```

---

## 验证结果

### 检查技能发现

```bash
python -m agent_framework.skills.lifecycle_cli list
```

应该看到所有已迁移的技能。

### 检查技能详情

```bash
python -m agent_framework.skills.lifecycle_cli show grill-me
```

### 运行健康检查

```bash
python -m agent_framework.skills.lifecycle_cli health-check
```

---

## 迁移示例

### 示例 1: 简单技能

**迁移前** (`SKILL.md`):

```markdown
# Grill Me

Interview user with dense questions.
```

**迁移后** (`SKILL.md`):

```markdown
---
name: grill-me
description: Interview user with dense, specific questions
version: 1.0
category: grilling
tags: [qa, interview, test]
---

# Grill Me

Interview user with dense, specific questions covering definitions, formulas, classifications, relationships, and applications.
```

### 示例 2: 带分类的技能

**迁移前**:

```markdown
# Advance Task

Update session state after each Q&A round.
```

**迁移后**:

```markdown
---
name: advance-task
description: Update session state after each Q&A round
version: 1.0
category: session
tags: [advance, continue, handoff]
---

# Advance Task

Update session state after each Q&A round by recording progress to Task.md and updating CONTEXT.md.
```

### 示例 3: 超长内容

**迁移前**:

```markdown
# Research Skill

This is a long research skill...

[200+ lines of content]
```

**迁移后**:

`SKILL.md`:
```markdown
---
name: research
description: Academic research assistance
version: 1.0
category: research
tags: [academic, paper, research]
---

# Research Skill

Academic research assistance for literature review, paper writing, and methodology design.

See [REFERENCE.md](REFERENCE.md) for detailed content.
```

`REFERENCE.md`:
```markdown
# Research Reference

[Original detailed content]
```

---

## 常见问题

### Q: 迁移后技能找不到？

A: 检查以下几点：
1. YAML frontmatter 格式正确
2. `name` 字段唯一且不为空
3. 文件名与 `name` 一致（推荐）
4. 运行 `python -m agent_framework.skills.lifecycle_cli health-check`

### Q: 迁移后路由失败？

A: 确保 `category` 字段与支持的 `task_type` 匹配：
- `grilling` → `grill-me`
- `qa` → `grill-you`
- `advance` → `advance-task`
- `review` → `review-session`
- `continue` → `continue-task`

### Q: 如何处理自定义分类？

A: 可以使用自定义 `category`，但需要添加自定义路由：

```python
middleware.add_route("custom-category", "my-custom-skill")
```

### Q: 迁移工具损坏了文件？

A: 使用备份恢复：

```bash
# 如果有备份
cp -r skills-backup/* skills/

# 或使用 git
git checkout HEAD -- skills/
```

---

## 回滚方案

### 使用 Git 回滚

```bash
# 查看变更
git diff skills/

# 回滚单个文件
git checkout HEAD -- skills/my-skill/SKILL.md

# 回滚所有变更
git reset --hard HEAD
```

### 使用备份恢复

```bash
# 从备份恢复
rm -rf skills/
cp -r skills-backup/ skills/
```

### 重新迁移

```bash
# 重新运行迁移工具
python -m agent_framework.skills.migrator_cli migrate-all
```

---

## 迁移后优化

### 1. 验证 Token 消耗

迁移后使用 `ContextOptimizer` 减少 Token 消耗：

```python
from agent_framework.skills.context_optimizer import ContextOptimizer

optimizer = ContextOptimizer(registry=registry)
metadata = optimizer.inject_metadata()

# 检查 Token 消耗
tokens = len(metadata) // 4
print(f"元数据注入: {tokens} tokens")
```

### 2. 测试技能执行

```bash
# 运行测试验证技能工作正常
pytest agent_framework/tests/integration/skills/ -v
```

### 3. 更新文档

更新技能相关的文档和示例。

---

## 相关文档

- [用户指南](user_guide.md)
- [API 文档](api_reference.md)
- [规范文档](../spec-feature/01-master-spec.md)
