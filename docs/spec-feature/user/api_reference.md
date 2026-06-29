# Agent Framework 技能系统 - API 参考

本文档提供技能系统所有公开 API 的详细参考。

---

## 目录

- [Skill Registry API](#skill-registry-api)
- [Middleware API](#middleware-api)
- [Context Optimizer API](#context-optimizer-api)
- [Observability API](#observability-api)
- [数据模型](#数据模型)

---

## Skill Registry API

### `SkillRegistry`

管理技能的发现、注册和查询。

#### 初始化

```python
from agent_framework.skills.registry import SkillRegistry
from pathlib import Path

registry = SkillRegistry(skills_dir=Path("skills/"))
```

#### 方法

##### `discover() -> None`

扫描技能目录，发现所有技能。

```python
registry.discover()
```

**异常**: 无

---

##### `register(metadata: SkillMetadata) -> None`

注册技能到注册表。

```python
from agent_framework.skills.models.metadata import SkillMetadata

metadata = SkillMetadata(
    name="my-skill",
    description="My skill description",
    version="1.0",
    category="general",
    tags=["utility"],
    file_path=Path("skills/my-skill/SKILL.md")
)
registry.register(metadata)
```

**参数**:
- `metadata`: 技能元数据

**异常**:
- `DuplicateSkillError`: 技能已存在时

---

##### `get(name: str) -> SkillMetadata`

按名称获取技能。

```python
skill = registry.get("grill-me")
```

**参数**:
- `name`: 技能名称

**返回**: `SkillMetadata`

**异常**:
- `SkillNotFoundError`: 技能不存在时

---

##### `find_by_category(category: str) -> List[SkillMetadata]`

按分类查询技能。

```python
grilling_skills = registry.find_by_category("grilling")
```

**参数**:
- `category`: 技能分类

**返回**: `List[SkillMetadata]` - 该分类下的所有技能

---

##### `list_all() -> List[SkillMetadata]`

列出所有已注册技能。

```python
all_skills = registry.list_all()
```

**返回**: `List[SkillMetadata]` - 所有技能列表

---

## Middleware API

### `SkillMiddleware`

负责技能路由和执行。

#### 初始化

```python
from agent_framework.skills.middleware import SkillMiddleware

middleware = SkillMiddleware(registry)
```

#### 方法

##### `route(state: Dict[str, Any]) -> str`

根据状态路由到合适的技能。

```python
state = {"task_type": "grilling"}
skill_name = middleware.route(state)
```

**参数**:
- `state`: 执行状态，可包含 `task_type` 和 `user_query`

**返回**: `str` - 技能名称

**异常**:
- `RouteNotFoundError`: 无法找到匹配的技能时

**路由优先级**:
1. 自定义路由映射
2. `task_type` 匹配
3. `user_query` 关键词匹配
4. 默认路由

---

##### `execute_skill(skill_name: str, context: SkillContext, loader: SkillLoader) -> SkillResult`

执行指定技能。

```python
from agent_framework.skills.models.context import SkillContext
from agent_framework.skills.loader import SkillLoader

context = SkillContext(session_path=Path("./"), state={})
loader = SkillLoader(registry)
result = middleware.execute_skill("grill-me", context, loader)
```

**参数**:
- `skill_name`: 技能名称
- `context`: 技能上下文
- `loader`: 技能加载器

**返回**: `SkillResult`

---

##### `add_route(task_type: str, skill_name: str) -> None`

添加自定义路由映射。

```python
middleware.add_route("custom", "my-skill")
```

**参数**:
- `task_type`: 任务类型
- `skill_name`: 技能名称

---

##### `add_interceptor(interceptor: Interceptor) -> None`

添加拦截器。

```python
from agent_framework.skills.middleware import LoggingInterceptor

middleware.add_interceptor(LoggingInterceptor())
```

**参数**:
- `interceptor`: 拦截器实例

---

## Context Optimizer API

### `ContextOptimizer`

优化上下文注入，减少 Token 消耗。

#### 初始化

```python
from agent_framework.skills.context_optimizer import ContextOptimizer

optimizer = ContextOptimizer(registry=registry)
```

#### 方法

##### `inject_metadata() -> str`

注入技能元数据到上下文。

```python
metadata = optimizer.inject_metadata()
```

**返回**: `str` - 包含所有技能元数据的字符串

**说明**: 只注入 YAML frontmatter 和目录，不注入完整内容

---

##### `should_load_full_content(skill_name: str, state: Dict[str, Any]) -> bool`

判断是否需要加载完整技能内容。

```python
state = {"task_type": "grilling"}
should_load = optimizer.should_load_full_content("grill-me", state)
```

**参数**:
- `skill_name`: 技能名称
- `state`: 执行状态

**返回**: `bool` - 是否需要加载完整内容

**判断条件**:
- 技能的 `category` 与 `task_type` 匹配
- 技能名称在 `user_query` 中出现
- 技能被显式标记为需要加载

---

## Observability API

### `TraceManager`

管理技能执行的链路追踪。

#### 初始化

```python
from agent_framework.observability.tracing import TraceManager

trace_manager = TraceManager()
```

#### 方法

##### `start_trace(context: Dict[str, Any]) -> str`

开始一个新的追踪。

```python
trace_id = trace_manager.start_trace({"session": "test-123"})
```

**参数**:
- `context`: 初始上下文信息

**返回**: `str` - 追踪 ID

---

##### `create_span(trace_id: str, skill_name: str, parent_span_id: Optional[str] = None) -> str`

创建一个 span。

```python
span_id = trace_manager.create_span(trace_id, "grill-me")
```

**参数**:
- `trace_id`: 追踪 ID
- `skill_name`: 技能名称
- `parent_span_id`: 父 span ID（可选）

**返回**: `str` - span ID

---

##### `end_span(trace_id: str, span_id: str, result: Dict[str, Any]) -> None`

结束一个 span。

```python
trace_manager.end_span(trace_id, span_id, {"success": True})
```

**参数**:
- `trace_id`: 追踪 ID
- `span_id`: span ID
- `result`: 执行结果

---

##### `get_trace(trace_id: str) -> Optional[TraceData]`

获取追踪数据。

```python
trace = trace_manager.get_trace(trace_id)
```

**参数**:
- `trace_id`: 追踪 ID

**返回**: `TraceData` 或 `None`

---

### `ErrorDiagnostics`

异常诊断和恢复建议。

#### 方法

##### `diagnose(exception_type: str, error_message: str, skill_name: str, context: Dict[str, Any]) -> ErrorRecord`

诊断异常并生成报告。

```python
error_record = diagnostics.diagnose(
    exception_type="ToolNotFoundError",
    error_message="Tool 'search' not found",
    skill_name="grill-me",
    context={"session": "/tmp/test"}
)
```

**参数**:
- `exception_type`: 异常类型
- `error_message`: 错误消息
- `skill_name`: 发生错误的技能名称
- `context`: 执行上下文

**返回**: `ErrorRecord`

---

### `ObservabilityDashboard`

可观测性数据汇总和统计。

#### 方法

##### `record_skill_call(skill_name: str) -> None`

记录技能调用。

```python
dashboard.record_skill_call("grill-me")
```

**参数**:
- `skill_name`: 技能名称

---

##### `record_error(error_record: ErrorRecord) -> None`

记录错误。

```python
dashboard.record_error(error_record)
```

**参数**:
- `error_record`: 错误记录

---

##### `get_error_stats() -> ErrorStats`

获取错误统计。

```python
stats = dashboard.get_error_stats()
```

**返回**: `ErrorStats`

---

##### `get_skill_ranking() -> List[SkillStats]`

获取技能排行（按调用次数）。

```python
ranking = dashboard.get_skill_ranking()
```

**返回**: `List[SkillStats]`

---

## 数据模型

### `SkillMetadata`

技能元数据。

```python
@dataclass
class SkillMetadata:
    name: str              # 技能名称
    description: str       # 技能描述
    version: str = "1.0"   # 版本号
    category: str = ""    # 分类
    tags: List[str] = field(default_factory=list)  # 标签
    file_path: Optional[Path] = None  # 文件路径
```

### `SkillContext`

技能执行上下文。

```python
@dataclass
class SkillContext:
    session_path: Path    # 会话目录
    state: Dict[str, Any]  # 执行状态
```

### `SkillResult`

技能执行结果。

```python
@dataclass
class SkillResult:
    success: bool              # 是否成功
    output: str                # 输出内容
    error: Optional[str] = None  # 错误信息
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
```

### `TraceData`

追踪数据。

```python
@dataclass
class TraceData:
    trace_id: str              # 追踪 ID
    skill_chain: List[str]      # 技能调用链
    timestamps: Dict[str, datetime]  # 时间戳
    state_transitions: List[StateTransition]  # 状态转换
```

### `ErrorRecord`

错误记录。

```python
@dataclass
class ErrorRecord:
    error_id: str              # 错误 ID
    error_type: str            # 错误类型
    severity: Severity         # 严重程度
    message: str               # 错误消息
    skill_name: str            # 技能名称
    timestamp: datetime        # 时间戳
    recovery_action: Optional[str] = None  # 恢复建议
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
```

---

## 异常类

### `DuplicateSkillError`

重复注册技能时抛出。

```python
from agent_framework.skills.registry import DuplicateSkillError

try:
    registry.register(metadata)
except DuplicateSkillError as e:
    print(f"技能已存在: {e}")
```

### `SkillNotFoundError`

技能不存在时抛出。

```python
from agent_framework.skills.registry import SkillNotFoundError

try:
    skill = registry.get("nonexistent")
except SkillNotFoundError as e:
    print(f"技能不存在: {e}")
```

### `RouteNotFoundError`

路由失败时抛出。

```python
from agent_framework.skills.middleware import RouteNotFoundError

try:
    skill = middleware.route({"task_type": "nonexistent"})
except RouteNotFoundError as e:
    print(f"路由失败: {e}")
```

---

## 相关文档

- [用户指南](user_guide.md)
- [迁移指南](migration_guide.md)
- [规范文档](../spec-feature/01-master-spec.md)
