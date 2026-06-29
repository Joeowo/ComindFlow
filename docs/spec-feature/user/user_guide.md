# Agent Framework 技能系统 - 用户指南

本文档介绍如何使用 ComindFlow Agent Framework 的技能系统。

---

## 快速开始

### 1. 创建技能

在 `skills/` 目录下创建技能子目录，并添加 `SKILL.md` 文件：

```bash
skills/
└── my-skill/
    └── SKILL.md
```

### 2. SKILL.md 格式

```markdown
---
name: my-skill
description: 我的技能描述
version: 1.0
category: general
tags: [utility, helper]
---

# My Skill

技能描述...

## Usage

使用场景说明...

## Examples

示例内容...
```

### 3. 使用技能系统

```python
from agent_framework.skills.registry import SkillRegistry
from agent_framework.skills.middleware import SkillMiddleware
from agent_framework.skills.loader import SkillLoader

# 初始化组件
registry = SkillRegistry(skills_dir=Path("skills/"))
registry.discover()

middleware = SkillMiddleware(registry)
loader = SkillLoader(registry)

# 路由和执行
state = {"task_type": "general"}
skill_name = middleware.route(state)
result = middleware.execute_skill(skill_name, context, loader)
```

---

## 技能系统概览

### 核心组件

| 组件 | 功能 | 文件 |
|------|------|------|
| **SkillRegistry** | 发现、注册、查询技能 | `registry.py` |
| **SkillLoader** | 按需加载、缓存技能 | `loader.py` |
| **SkillMiddleware** | 路由、拦截、执行技能 | `middleware.py` |
| **ContextOptimizer** | 元数据注入、按需加载判断 | `context_optimizer.py` |
| **BudgetManager** | Token 预算管理 | `budget_manager.py` |

### 工作流程

```
用户请求 → SkillMiddleware 路由 → ContextOptimizer 优化 → SkillLoader 加载 → 执行技能 → 返回结果
                        ↓
                   TraceManager 追踪
                        ↓
                   ErrorDiagnostics 诊断
```

---

## 使用技能

### 基本使用

#### 1. 技能发现和查询

```python
from agent_framework.skills.registry import SkillRegistry

registry = SkillRegistry(skills_dir=Path("skills/"))
registry.discover()

# 列出所有技能
all_skills = registry.list_all()
for skill in all_skills:
    print(f"{skill.name}: {skill.description}")

# 按分类查询
grilling_skills = registry.find_by_category("grilling")

# 获取特定技能
skill = registry.get("grill-me")
```

#### 2. 技能路由

```python
from agent_framework.skills.middleware import SkillMiddleware

middleware = SkillMiddleware(registry)

# 通过 task_type 路由
state = {"task_type": "grilling"}
skill_name = middleware.route(state)

# 通过 user_query 路由（关键词匹配）
state = {"user_query": "Can you test me on economics?"}
skill_name = middleware.route(state)
```

#### 3. 技能执行

```python
from agent_framework.skills.loader import SkillLoader
from agent_framework.skills.models.context import SkillContext

loader = SkillLoader(registry)
context = SkillContext(session_path=Path("./"), state={})

result = middleware.execute_skill(skill_name, context, loader)

if result.success:
    print(f"技能执行成功: {result.output}")
else:
    print(f"技能执行失败: {result.error}")
```

### 并行执行

```python
from agent_framework.skills.executor import ParallelSkillExecutor

executor = ParallelSkillExecutor(middleware)

# 并行执行多个技能
contexts = [SkillContext(...) for _ in range(3)]
skill_names = ["grill-me", "grill-you", "advance-task"]

results = executor.execute_parallel(skill_names, contexts, loader)

for i, result in enumerate(results):
    print(f"技能 {skill_names[i]}: {result.success}")
```

---

## 管理技能

### 验证 SKILL.md

```bash
# 使用 CLI 验证技能
python -m agent_framework.skills.validator_cli validate skills/my-skill/

# 验证所有技能
python -m agent_framework.skills.validator_cli validate-all
```

### 迁移旧格式

```bash
# 迁移单个技能到新规范
python -m agent_framework.skills.migrator_cli migrate skills/my-skill/

# 迁移所有技能
python -m agent_framework.skills.migrator_cli migrate-all
```

### 查看技能统计

```bash
# 查看所有技能统计
python -m agent_framework.skills.lifecycle_cli list

# 查看技能详情
python -m agent_framework.skills.lifecycle_cli show grill-me

# 检查技能健康状态
python -m agent_framework.skills.lifecycle_cli health-check
```

---

## 可观测性

### 查看链路追踪

```python
from agent_framework.observability.tracing import TraceManager

trace_manager = TraceManager()

# 开始追踪
trace_id = trace_manager.start_trace({"session": "test-123"})

# 创建 span
span_id = trace_manager.create_span(trace_id, "grill-me")
# ... 执行技能 ...
trace_manager.end_span(trace_id, span_id, {"success": True})

# 获取追踪数据
trace = trace_manager.get_trace(trace_id)
print(f"技能链: {trace.skill_chain}")
```

### 分析异常

```python
from agent_framework.observability.diagnostics import ErrorDiagnostics

diagnostics = ErrorDiagnostics()

# 诊断异常
error_record = diagnostics.diagnose(
    exception_type="ToolNotFoundError",
    error_message="Tool 'search' not found",
    skill_name="grill-me",
    context={"session": "/tmp/test"}
)

print(f"严重程度: {error_record.severity}")
print(f"恢复建议: {error_record.recovery_action}")
```

### Dashboard 使用

```python
from agent_framework.observability.dashboard import ObservabilityDashboard

dashboard = ObservabilityDashboard()

# 记录技能调用
dashboard.record_skill_call("grill-me")

# 获取统计
stats = dashboard.get_error_stats()
print(f"总错误数: {stats.total_errors}")

# 获取技能排行
ranking = dashboard.get_skill_ranking()
for item in ranking:
    print(f"{item.skill_name}: {item.call_count} 次调用")
```

---

## 上下文优化

### 元数据注入

```python
from agent_framework.skills.context_optimizer import ContextOptimizer

optimizer = ContextOptimizer(registry=registry)

# 注入元数据（只包含 frontmatter 和目录）
metadata = optimizer.inject_metadata()

# 元数据可以被添加到 LLM 上下文中
llm_context = f"{system_prompt}\n\n{metadata}"
```

### 按需加载

```python
# 判断是否需要加载完整内容
state = {"task_type": "grilling"}

if optimizer.should_load_full_content("grill-me", state):
    # 加载完整内容
    content = loader.load_skill("grill-me")
else:
    # 只使用元数据
    pass
```

### 预算管理

```python
from agent_framework.skills.budget_manager import BudgetManager

budget = BudgetManager(total_budget=8000, metadata_reserve=1000)

# 检查是否可以加载
if budget.can_load("grill-me", 2000):
    content = loader.load_skill("grill-me")
    budget.record_load("grill-me", 2000)

# 查看预算状态
status = budget.get_status()
print(f"可用预算: {status['available_budget']} tokens")
```

---

## 故障排除

### 常见问题

**Q: 技能没有被发现？**

A: 检查以下几点：
1. 技能目录下是否有 `SKILL.md` 文件
2. `SKILL.md` 是否包含有效的 YAML frontmatter
3. `name` 字段是否唯一且不为空

**Q: 路由失败？**

A: 确保使用的 `task_type` 或 `user_query` 关键词与技能匹配：
- 使用 `middleware.add_route()` 添加自定义路由
- 检查 `DEFAULT_ROUTE_MAPPING` 中是否有对应的 `task_type`

**Q: Token 消耗过高？**

A: 使用 `ContextOptimizer` 的元数据注入功能：
- 只注入元数据，不注入完整内容
- 使用按需加载，只加载需要的技能
- 配置 `BudgetManager` 限制 Token 消耗

**Q: 技能执行失败？**

A: 检查以下几点：
1. 技能文件是否有效
2. 使用 `SkillValidator` 验证 SKILL.md 格式
3. 查看 `ErrorDiagnostics` 获取详细诊断信息

### 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查技能注册表
registry = SkillRegistry(skills_dir=Path("skills/"))
registry.discover()
print(f"已注册 {len(registry.list_all())} 个技能")

# 测试路由
from agent_framework.skills.middleware import SkillMiddleware
middleware = SkillMiddleware(registry)
try:
    skill = middleware.route({"task_type": "test"})
except Exception as e:
    print(f"路由失败: {e}")
```

---

## 最佳实践

### 1. 技能设计

- 保持技能职责单一
- 使用清晰的描述和分类
- 添加相关标签便于发现

### 2. 性能优化

- 使用元数据注入减少 Token 消耗
- 实现按需加载避免不必要的内容加载
- 配置合理的预算限制

### 3. 错误处理

- 使用拦截器统一处理异常
- 记录详细的错误信息用于诊断
- 实现适当的降级策略

### 4. 可观测性

- 为关键操作添加追踪
- 记录重要的业务指标
- 定期检查 Dashboard 了解系统状态

---

## 附录

### 支持的 task_type

| task_type | 默认技能 | 描述 |
|-----------|----------|------|
| `grilling` | grill-me | 问答测试 |
| `qa` | grill-you | 问题回答 |
| `advance` | advance-task | 任务进度更新 |
| `review` | review-session | 会话审查 |
| `continue` | continue-task | 继续任务 |

### 支持的关键词

| 关键词 | 技能 | 描述 |
|--------|------|------|
| `grill` | grill-me | 问答相关 |
| `interview` | grill-me | 访谈相关 |
| `review` | review-session | 审查相关 |
| `handoff` | advance-task | 移交相关 |

### 相关文档

- [API 文档](api_reference.md)
- [迁移指南](migration_guide.md)
- [规范文档](../spec-feature/01-master-spec.md)
