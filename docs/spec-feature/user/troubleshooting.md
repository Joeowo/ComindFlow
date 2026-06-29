# Agent Framework 技能系统 - 故障排除

本文档提供常见问题的诊断和解决方案。

---

## 目录

- [常见问题](#常见问题)
- [调试技巧](#调试技巧)
- [错误代码](#错误代码)
- [性能问题](#性能问题)
- [日志分析](#日志分析)

---

## 常见问题

### 技能发现

#### 问题: 技能没有被发现

**症状**: `registry.list_all()` 返回空列表

**可能原因**:
1. 技能目录路径不正确
2. `SKILL.md` 文件不存在
3. YAML frontmatter 格式错误
4. `name` 字段为空

**解决方案**:

```bash
# 1. 检查目录结构
ls -la skills/

# 2. 验证 SKILL.md 格式
python -m agent_framework.skills.validator_cli validate skills/my-skill/

# 3. 检查 YAML frontmatter
head -n 10 skills/my-skill/SKILL.md
```

**示例修复**:

```yaml
---
name: my-skill       # 确保 name 不为空
description: ...    # 确保 description 存在
---
```

#### 问题: 技能重复注册

**症状**: `DuplicateSkillError` 异常

**可能原因**:
- 多个技能使用相同的 `name`
- 同一技能被多次注册

**解决方案**:

```bash
# 检查是否有重复的技能名称
python -c "
from agent_framework.skills.registry import SkillRegistry
from pathlib import Path
registry = SkillRegistry(skills_dir=Path('skills/'))
registry.discover()
names = [s.name for s in registry.list_all()]
print('重复名称:', [name for name in names if names.count(name) > 1])
"
```

---

### 路由问题

#### 问题: 路由找不到技能

**症状**: `RouteNotFoundError` 异常

**可能原因**:
1. `task_type` 不在默认映射中
2. 没有添加自定义路由
3. 技能没有注册

**解决方案**:

```python
# 1. 检查默认路由映射
from agent_framework.skills.middleware import SkillMiddleware
print(SkillMiddleware.DEFAULT_ROUTE_MAPPING)

# 2. 添加自定义路由
middleware.add_route("custom-type", "my-skill")

# 3. 验证技能已注册
skills = registry.list_all()
print(f"已注册 {len(skills)} 个技能")
```

#### 问题: 路由到错误的技能

**症状**: 路由结果与预期不符

**可能原因**:
- 关键词匹配优先级问题
- 多个技能具有相同的关键词

**解决方案**:

```python
# 明确指定路由
middleware.add_route("desired-type", "target-skill")

# 或者使用唯一的关键词
# 在 SKILL.md 中使用独特的描述和标签
```

---

### 执行问题

#### 问题: 技能执行失败

**症状**: `SkillResult.success = False`

**可能原因**:
1. 技能文件加载失败
2. 拦截器抛出异常
3. 上下文参数不正确

**解决方案**:

```python
# 1. 检查技能文件
from agent_framework.skills.validator_cli import validate
validate("skills/my-skill/")

# 2. 测试无拦截器执行
result = middleware.execute_skill("my-skill", context, loader)

# 3. 检查错误信息
if not result.success:
    print(f"错误: {result.error}")
```

#### 问题: 技能执行超时

**症状**: 执行时间过长或挂起

**可能原因**:
1. 技能内容过大
2. LLM 调用超时
3. 资源争用

**解决方案**:

```python
# 1. 检查技能内容大小
import os
size = os.path.getsize("skills/my-skill/SKILL.md")
print(f"文件大小: {size} bytes")

# 2. 使用元数据注入替代完整加载
optimizer = ContextOptimizer(registry)
metadata = optimizer.inject_metadata()

# 3. 配置超时时间
# 在调用 LLM 时设置合理的超时
```

---

### 性能问题

#### 问题: Token 消耗过高

**症状**: LLM 上下文超出限制

**诊断**:

```python
from agent_framework.skills.context_optimizer import ContextOptimizer

optimizer = ContextOptimizer(registry=registry)

# 检查元数据注入大小
metadata = optimizer.inject_metadata()
print(f"元数据 Token 数: {len(metadata) // 4}")

# 检查完整内容大小
from agent_framework.skills.loader import SkillLoader
loader = SkillLoader(registry)
total = 0
for skill in registry.list_all():
    content = loader.load_skill(skill.name)
    total += len(content) // 4
print(f"完整内容 Token 数: {total}")
```

**解决方案**:

1. 使用元数据注入而非完整加载
2. 实现按需加载
3. 配置预算管理器

```python
from agent_framework.skills.budget_manager import BudgetManager

budget = BudgetManager(total_budget=8000, metadata_reserve=1000)
if budget.can_load("skill-name", estimated_tokens):
    # 加载技能
    pass
```

#### 问题: 响应时间慢

**症状**: 技能执行超过 2 秒

**诊断**:

```python
import time

start = time.time()
result = middleware.execute_skill("skill-name", context, loader)
elapsed = time.time() - start

print(f"执行时间: {elapsed:.2f}秒")
```

**解决方案**:

1. 使用并行执行多个技能
2. 优化技能内容大小
3. 启用缓存

```python
from agent_framework.skills.executor import ParallelSkillExecutor

executor = ParallelSkillExecutor(middleware)
results = executor.execute_parallel(skill_names, contexts, loader)
```

---

## 调试技巧

### 启用详细日志

```python
import logging
from loguru import logger

# 设置日志级别
logger.add("debug.log", level="DEBUG")

# 或使用标准 logging
logging.basicConfig(level=logging.DEBUG)
```

### 检查组件状态

```python
# 1. 检查注册表
registry = SkillRegistry(skills_dir=Path("skills/"))
registry.discover()
print(f"已发现 {len(registry.list_all())} 个技能")

# 2. 检查加载器
loader = SkillLoader(registry)
print(f"已加载 {len(loader._cache)} 个技能")

# 3. 检查中间件
middleware = SkillMiddleware(registry)
print(f"自定义路由: {middleware._route_mapping}")
```

### 使用可观测性工具

```python
from agent_framework.observability.tracing import TraceManager
from agent_framework.observability.diagnostics import ErrorDiagnostics

# 启用追踪
trace_manager = TraceManager()
trace_id = trace_manager.start_trace({"debug": True})

# 执行操作...
span_id = trace_manager.create_span(trace_id, "operation-name")
trace_manager.end_span(trace_id, span_id, {"result": "success"})

# 分析追踪
trace = trace_manager.get_trace(trace_id)
print(f"技能链: {trace.skill_chain}")
print(f"状态转换: {trace.state_transitions}")
```

### 单元测试调试

```bash
# 运行特定测试
pytest agent_framework/tests/unit/skills/test_registry.py -v

# 使用 pdb 调试
pytest agent_framework/tests/unit/skills/test_registry.py --pdb

# 查看输出
pytest agent_framework/tests/unit/skills/test_registry.py -v -s
```

---

## 错误代码

### 异常类型

| 异常 | 模块 | 说明 |
|------|------|------|
| `DuplicateSkillError` | registry | 技能已存在 |
| `SkillNotFoundError` | registry | 技能不存在 |
| `SkillLoadError` | loader | 技能加载失败 |
| `RouteNotFoundError` | middleware | 路由失败 |
| `SkillExecutionError` | middleware | 技能执行失败 |

### 错误严重程度

| 级别 | 说明 | 示例 |
|------|------|------|
| **P0** | 可用性异常 | 工具未找到、状态转换失败 |
| **P1** | 依赖异常 | 模块依赖问题、外部服务不可用 |
| **P2** | 性能异常 | 执行缓慢、资源消耗高 |

### 错误诊断

```python
from agent_framework.observability.diagnostics import ErrorDiagnostics

diagnostics = ErrorDiagnostics()

error_record = diagnostics.diagnose(
    exception_type="ToolNotFoundError",
    error_message="Tool 'search' not found",
    skill_name="grill-me",
    context={"session": "/tmp/test"}
)

print(f"严重程度: {error_record.severity}")
print(f"恢复建议: {error_record.recovery_action}")
```

---

## 日志分析

### 日志位置

```
agent_framework/
├── logs/              # 应用日志
├── debug.log          # 调试日志
└── error.log          # 错误日志
```

### 日志格式

日志使用结构化格式：

```json
{
  "timestamp": "2026-06-29T20:00:00.000Z",
  "level": "INFO",
  "module": "skills.registry",
  "message": "Skill registered",
  "context": {
    "name": "grill-me"
  }
}
```

### 常见日志模式

#### 技能注册

```
INFO | skills.registry | Skill registered | name=grill-me
INFO | skills.registry | Discovery complete | count=5
```

#### 技能加载

```
INFO | skills.loader | Skill loaded | name=grill-me
DEBUG | skills.loader | Skill loaded from cache | name=grill-me
```

#### 技能执行

```
INFO | skills.middleware | Skill execution started | skill=grill-me
INFO | skills.middleware | Skill execution completed | skill=grill-me, success=True
```

#### 错误日志

```
ERROR | skills.middleware | Skill execution failed | skill=grill-me, error=Tool not found
ERROR | observability.diagnostics | Error diagnosed | severity=P0, recovery_action=Check tool registration
```

---

## 性能分析

### 运行性能测试

```bash
# 运行性能基准测试
pytest agent_framework/tests/performance/benchmarks/ --benchmark-only

# 生成性能报告
pytest agent_framework/tests/performance/benchmarks/ --benchmark-json=benchmark.json
```

### 分析 Token 消耗

```bash
# 运行 Token 消耗测试
pytest agent_framework/tests/performance/benchmarks/test_token_consumption.py -v -s

# 查看详细输出
pytest agent_framework/tests/performance/benchmarks/test_token_consumption.py::TestTokenConsumptionBaseline::test_baseline_10_skills -v -s
```

### 监控响应时间

```python
import time

def measure_execution(func, *args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - start
    print(f"{func.__name__} 执行时间: {elapsed:.3f}秒")
    return result

# 使用
measure_execution(middleware.execute_skill, "skill-name", context, loader)
```

---

## 获取帮助

### 社区资源

- **文档**: [docs/spec-feature/](../spec-feature/)
- **规范**: [01-master-spec.md](../spec-feature/01-master-spec.md)
- **GitHub Issues**: [项目 Issues 页面]

### 报告问题

报告问题时请包含：

1. 错误消息和堆栈跟踪
2. 最小复现代码
3. 环境信息（Python 版本、操作系统）
4. 相关日志输出

### 调试模式

启用调试模式获取更多信息：

```python
import os
os.environ["DEBUG"] = "1"

# 或在运行时
DEBUG=1 python your_script.py
```

---

## 相关文档

- [用户指南](user_guide.md)
- [API 文档](api_reference.md)
- [迁移指南](migration_guide.md)
