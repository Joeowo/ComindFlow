# Agent Skills/Workflow 优化 Agent 框架调研报告

**调研日期**: 2025-06-17
**调研主题**: 使用 agent skills/workflow 优化 agent 框架本身的研究与 benchmark

---

## 执行摘要

本调研针对您提出的核心问题——**如何通过 agent 架构、workflow 设计、任务上下文管理来优化模型处理复杂软件工程任务的能力**——进行了全面的文献检索和分析。

**关键发现**:
1. **任务分解是当前 Agent 系统的核心瓶颈** - 多篇论文指出，虽然模型能力在提升，但"scaffolding"（任务分解和编排架构）是亟需创新的领域
2. **Agent Skills 范式正在兴起** - 从单体模型转向模块化、可组合的技能系统成为重要趋势
3. **Workflow 优化形成完整的研究体系** - IBM 等机构的综述显示该领域已有静态优化和动态优化两大分支
4. **专门的 Benchmark 体系正在建立** - SWE-bench、AgentBench、Meta-Agent Challenge 等为评估提供了基础

---

## 一、核心问题分析

### 1.1 问题定义

您提出的观察被多篇论文所证实：

> "当前模型倾向于直接解决问题，而忽视架构兼容、设计模式等问题"
>
> —— *CMU-CS-25-132, "An LLM-Based Approach to Supporting Software Engineering Tasks"*

软件工程任务天然需要多阶段处理：
1. **理解设计原则** (SOLID、设计模式、架构风格)
2. **分析仓库** (代码结构、依赖关系、技术栈识别)
3. **应用设计决策** (选择合适的设计模式、架构方案)
4. **编码实现** (遵循既定设计进行编码)

### 1.2 研究现状

当前研究将这些步骤分离为不同的 **Agent Skills** 或 **Workflow 节点**，通过编排框架协调执行。

---

## 二、核心论文分析

### 2.1 Agent Skills 基础理论

#### **Agent Skills for Large Language Models** (arXiv:2602.12430, 2026)

**论文链接**: https://arxiv.org/abs/2602.12430

**核心贡献**:
- 定义了 Agent Skills 范式：从单体语言模型向模块化、技能增强的 Agent 转变
- Skills 是"可组合的指令、代码和资源包，Agent 可按需加载"
- 提出 SKILL.md 规范和渐进式上下文加载
- 与 Model Context Protocol (MCP) 集成

**研究维度**:
1. **架构基础**: SKILL.md 规范、渐进式上下文加载
2. **技能获取**: 强化学习、自主技能发现 (SEAgent)、组合式技能合成
3. **规模化部署**: CUA (Computer Use Agent) 栈、OSWorld/SWE-bench 进展
4. **安全性**: 26.1% 社区技能存在漏洞，提出四层权限模型

**关键洞察**:
> "Agent skills enable dynamic capability extension without retraining"
>
> 这为您的问题提供了答案——通过将软工设计原则封装为可重用的 Skills，避免每次都重新推理

---

#### **SoK: Agentic Skills — Beyond Tool Use** (arXiv:2602.20867)

**论文链接**: https://arxiv.org/html/2602.20867v1

**核心定义**:
- **Skill**: 可重用、可调用的模块，封装了动作序列/策略
- 区别于简单 Tool Use，Skills 包含多步骤工作流和领域知识

---

### 2.2 Workflow 优化框架

#### **HAWK: A Hierarchical Workflow Framework** (arXiv:2507.04067, 2025)

**论文链接**: https://arxiv.org/abs/2507.04067

**架构设计**: 五层架构
```
┌─────────────────────────────────────────┐
│           User Layer (用户接口)          │
├─────────────────────────────────────────┤
│      Workflow Layer (工作流编排)         │
│    ├── Task Parsing (任务解析)           │
│    ├── Workflow Orchestration (编排)    │
│    └── Adaptive Scheduling (自适应调度) │
├─────────────────────────────────────────┤
│       Operator Layer (算子层)            │
├─────────────────────────────────────────┤
│        Agent Layer (代理层)              │
├─────────────────────────────────────────┤
│      Resource Layer (资源抽象)          │
│    ├── Data Sources                     │
│    ├── LLMs                             │
│    ├── Devices                          │
│    └── Third-party Services             │
└─────────────────────────────────────────┘
```

**核心创新**:
- 16 个标准化接口实现跨平台互操作
- 实时反馈驱动的自适应调度
- 资源层的统一抽象简化跨域信息检索

---

#### **IBM Survey: From Static Templates to Dynamic Runtime Graphs**

**论文链接**: https://arxiv.org/abs/2603.22386
**GitHub 仓库**: https://github.com/IBM/awesome-agentic-workflow-optimization

**分类体系**:

| 维度 | 子类别 | 代表论文 |
|------|--------|----------|
| **静态优化** | 离线模板搜索 | AFlow, A²Flow, SEW |
| | 节点级优化 | DSPy, CAPO, GEPA |
| | 结构+配置联合优化 | Multi-Agent Design, Maestro |
| | 可验证性 | MermaidFlow, VFlow |
| **动态优化** | 选择和剪枝 | AgentDropout, DAGP, SkillOrchestra |
| | 先构建后执行 | AutoFlow, WorkflowLLM, ScoreFlow |
| | 执行中编辑 | DyFlow, EvoFlow, DebFlow |

**关键洞察**:
> Workflow 结构的确定时机（静态 vs 动态）是优化策略的核心分界点

---

### 2.3 Meta-Agent 与自我优化

#### **The Meta-Agent Challenge** (arXiv:2606.04455)

**论文链接**: https://arxiv.org/html/2606.04455v1

**评估框架**: 测试 Code Agent 自主设计、实现和改进自身的能力

#### **Meta-Benchmark for Self-Improvement** (NeurIPS 2024)

**论文链接**: https://neurips.cc/virtual/2024/103346

**核心机制**: 顶层 Agent 目标是提升参考 Agent 在各任务上的表现

---

### 2.4 上下文管理

#### **Graph of Agents** (arXiv:2509.21848)

**论文链接**: https://arxiv.org/html/2509.21848v1

**核心思想**: 多 Agent 系统通过辅助 LLM 重构和压缩输入来解决长上下文问题

#### **Chain-of-Agents** (Google Research)

**论文链接**: https://research.google/blog/chain-of-agents-large-language-models-collaborating-on-long-context-tasks/

**框架特点**:
- 无需训练、任务无关、高度可解释
- 通过 LLM 协作解决长上下文任务

---

### 2.5 软件工程专用研究

#### **CMU: An LLM-Based Approach to Supporting Software Engineering Tasks**

**论文链接**: http://ra.adm.cs.cmu.edu/anon/2025/CMU-CS-25-132.pdf

**核心贡献**: 任务分解使复杂工程任务可管理化，促进模块化和系统化处理

#### **Designing LLM-based Multi-Agent Systems for Software Engineering**

**论文链接**: https://arxiv.org/html/2511.08475v1

**研究内容**: 根据 Liu 等人的 LLM Agent 架构模式分类系统，对设计模式进行分类

---

## 三、Benchmark 体系

### 3.1 软件工程专用 Benchmark

#### **SWE-bench 系列**

| Benchmark | 特点 | 链接 |
|-----------|------|------|
| **SWE-bench** | 基于 GitHub Issues + 仓库上下文生成 Patch | https://www.swebench.com/ |
| **SWE-bench Pro** | 扩展至 41 仓库的 1,865 个问题 | - |
| **SWE-MERA** | 动态 Benchmark，可重现透明的评估环境 | https://arxiv.org/html/2507.11059v1 |
| **SWE-bench Verified** | OpenAI 人工验证子集，更可靠的评估 | https://openai.com/index/introducing-swe-bench-verified/ |

**评估目标**: 系统是否能将 GitHub Issue + 仓库上下文转换为通过测试的 Patch

#### **AgentBench** (ICLR 2026)

**论文链接**: https://arxiv.org/pdf/2308.03688
**GitHub**: https://github.com/THUDM/AgentBench

**特点**:
- 多维度 Benchmark，8 个不同环境
- 评估 LLM-as-Agent 的推理和决策能力
- 测试多轮开放场景
- 评估了 25-29 个不同 LLM

#### **MultiAgentBench**

**特点**: 首个综合评估多 Agent 系统协作和竞争能力的 Benchmark

---

### 3.2 自我优化 Benchmark

#### **Meta-Agent Challenge**

**评估维度**:
- 自主设计能力
- 自主实现能力
- 自我改进能力

#### **Benchmark-Gated Updates**

**论文链接**: https://medium.com/@dilipksah/the-strategic-future-of-self-improving-ai-agents-39093a6e0a30

**机制**: 在接受 Agent 改进前，通过验证的 Benchmark 要求

---

## 四、技术路线演进

### 4.1 Workflow 优化方法演进

```
2024年初                    2024年中                    2025年
┌─────────────┐           ┌─────────────┐           ┌─────────────┐
│  Static     │           │  Dynamic    │           │  Self-      │
│  Templates  │  ──────>  │  Graphs     │  ──────>  │  Improving  │
│             │           │             │           │  Agents     │
└─────────────┘           └─────────────┘           └─────────────┘
     │                         │                         │
     └─ 固定工作流              └─ 运行时自适应             └─ 元优化
```

### 4.2 Agent Skills 范式演进

```
Monolithic LLM          Tool Use              Agent Skills
     │                      │                      │
     ├─ 所有能力在模型内     ├─ 外部函数调用         ├─ 多步骤技能封装
     ├─ 需要重新训练         ├─ 单次操作            ├─ 可组合/重用
     └─ 上下文受限           └─ 缺乏领域知识         └─ 渐进式加载
```

---

## 五、核心架构模式

### 5.1 模块化 Agent 设计

#### **AgentSquare** (arXiv:2410.06153)

**论文链接**: https://arxiv.org/abs/2410.06153

**四大基础模块**:
```
┌─────────────────────────────────────────────────────┐
│                   AgentSquare                       │
├─────────────┬─────────────┬──────────┬─────────────┤
│  Planning   │  Reasoning  │  Tool    │   Policy    │
│  Module     │   Module    │ Module   │   Module    │
│  (任务规划) │   (推理)    │ (工具)   │   (策略)    │
└─────────────┴─────────────┴──────────┴─────────────┘
```

#### **AgentForge** (arXiv:2601.13383)

**论文链接**: https://arxiv.org/abs/2601.13383

**特点**: 轻量级模块化框架，6 个内置技能（Web 抓取、数据分析、内容生成等）

---

### 5.2 层次化 Multi-Agent 架构

```
                    ┌──────────────────┐
                    │   Meta Agent     │
                    │  (任务分解/调度)   │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐         ┌────▼────┐        ┌────▼────┐
   │ Design  │         │ Code    │        │ Test    │
   │ Agent   │         │ Agent   │        │ Agent   │
   └────┬────┘         └────┬────┘        └────┬────┘
        │                    │                    │
   ┌────▼────┐         ┌────▼────┐        ┌────▼────┐
   │ SOLID   │         │ syntax  │        │ unit    │
   │ Skills  │         │ Skills  │        │ Skills  │
   └─────────┘         └─────────┘        └─────────┘
```

---

### 5.3 软件工程任务工作流示例

基于您提出的需求，一个理想的 Workflow 应该是：

```
┌─────────────────────────────────────────────────────────────────┐
│                     软件工程任务 Workflow                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │  Phase 1:       │ -> │  Phase 2:       │ -> │  Phase 3:   │ │
│  │  设计原则分析   │    │  仓库分析       │    │  设计决策   │ │
│  │  - SOLID 解读   │    │  - 代码结构     │    │  - 模式选择 │ │
│  │  - 模式识别     │    │  - 依赖分析     │    │  - 架构设计 │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│                                  │                     │        │
│                                  └──────────┬──────────┘        │
│                                             │                   │
│                                  ┌──────────▼──────────┐        │
│                                  │   共享上下文仓库     │        │
│                                  │   - 设计文档         │        │
│                                  │   - 架构决策记录     │        │
│                                  └─────────────────────┘        │
│                                             │                   │
│                                  ┌──────────▼──────────┐        │
│                                  │  Phase 4: 编码实现  │        │
│                                  │  - 遵循设计决策     │        │
│                                  │  - 设计模式应用     │        │
│                                  └─────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 六、实用框架与工具

### 6.1 LangChain/LangGraph

| 资源 | 链接 |
|------|------|
| Workflows and Agents 文档 | https://docs.langchain.com/oss/python/langgraph/workflows-agents |
| LangGraph 主页 | https://www.langchain.com/langgraph |
| Multi-Agent Workflows | https://www.langchain.com/blog/langgraph-multi-agent-workflows |
| arXiv 论文 (2024.12) | https://arxiv.org/pdf/2412.03801 |

**特点**:
- 有预定代码路径的 Workflows
- 动态引导自身进程的 Agents
- 状态机、内存、人在回路模式

---

### 6.2 上下文工程最佳实践

| 来源 | 链接 | 核心观点 |
|------|------|----------|
| Anthropic | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | Write, Select, Compress, Isolate |
| LangChain | https://www.langchain.com/blog/context-engineering-for-agents | 上下文工程四大策略 |
| Google Research | Chain-of-Agents | 长上下文任务中的 Agent 协作 |

---

### 6.3 自动优化工具

| 工具 | 链接 | 特点 |
|------|------|------|
| Opik Agent Optimizer | https://www.comet.com/site/blog/automated-prompt-engineering/ | 框架无关的 SDK |
| Mpco (Meta-Prompted Code Optimization) | https://arxiv.org/html/2508.01443v2 | 自动生成任务特定 Prompt |

---

## 七、研究趋势与未来方向

### 7.1 当前趋势 (2024-2025)

1. **从静态到动态**: 静态模板搜索 → 运行时动态图生成
2. **从单体到模块**: 单体 LLM → Skills + MCP
3. **从单 Agent 到 Multi-Agent**: 协作、竞争、层次化
4. **从人工优化到自我优化**: Meta-Agent 自动设计子 Agent

### 7.2 开放挑战

基于 IBM Survey 和 Agent Skills 论文：

| 挑战 | 描述 |
|------|------|
| **跨平台技能可移植性** | Skills 如何在不同框架间迁移 |
| **基于能力的权限模型** | 根据 Skill 能力动态授予权限 |
| **幻觉缓解** | Workflow 层面的真实性保证 |
| **实时性能调优** | 运行时动态调整策略 |
| **跨域适应性** | 跨越不同领域的知识迁移 |
| **安全性** | 26.1% 社区技能存在漏洞 |
| **评估标准化** | 缺乏统一的 Workflow 评估标准 |

### 7.3 未来研究方向

1. **软工设计原则的技能化**: 将 SOLID、设计模式等封装为标准 Skills
2. **上下文感知的 Workflow**: 根据代码仓库特性动态调整工作流
3. **自我演进架构**: Agent 能够根据反馈自动优化其组织结构
4. **人机协作模式**: 在关键设计决策点引入专家验证

---

## 八、推荐资源

### 8.1 必读论文

1. **Agent Skills for LLMs** (arXiv:2602.12430) - 技能范式基础
2. **IBM Workflow Optimization Survey** (arXiv:2603.22386) - Workflow 优化全景
3. **HAWK Framework** (arXiv:2507.04067) - 层次化架构设计
4. **The Meta-Agent Challenge** (arXiv:2606.04455) - 自我优化评估

### 8.2 重要代码库

| 仓库 | 链接 | 用途 |
|------|------|------|
| IBM/awesome-agentic-workflow-optimization | https://github.com/IBM/awesome-agentic-workflow-optimization | Workflow 优化论文合集 |
| THUDM/AgentBench | https://github.com/THUDM/AgentBench | Agent 能力 Benchmark |
| luo-junyu/awesome-agent-papers | https://github.com/luo-junyu/awesome-agent-papers | Agent 论文合集 |
| YoungDubbyDu/LLM-Agent-Optimization | https://github.com/YoungDubbyDu/LLM-Agent-Optimization | Agent 优化论文 |

### 8.3 实践资源

1. **LangGraph 文档** - 构建状态化多 Agent 系统
2. **Anthropic Context Engineering** - 上下文管理最佳实践
3. **SWE-bench** - 软件工程任务评估

---

## 九、核心结论

### 9.1 对您问题的回答

您提出的核心观察——**"模型倾向于直接解决问题而不考虑架构和设计模式"**——已经被学术界充分认识并正在通过以下方式解决：

1. **任务分解 (Task Decomposition)**: 将复杂任务分解为专门的 Agent 或 Skills
2. **Workflow 编排**: 使用 HAWK 等框架协调多个 Agent 执行
3. **上下文管理**: 通过 Graph of Agents、Chain-of-Agents 等处理长上下文
4. **模块化设计**: AgentSquare 等框架提供标准化模块接口

### 9.2 实践建议

基于调研结果，对于您的场景：

1. **将软工设计原则封装为 Skills**:
   - `solid-analysis` skill: 分析代码是否符合 SOLID
   - `pattern-recommendation` skill: 基于上下文推荐设计模式
   - `architectural-review` skill: 审查架构兼容性

2. **建立层次化 Workflow**:
   - Meta Agent: 任务规划和分解
   - Specialized Agents: 设计分析、代码审查、实现
   - 共享上下文: 设计决策记录 (ADR)

3. **使用标准化 Benchmark**:
   - SWE-bench 验证整体能力
   - Meta-Agent Challenge 评估自我改进

---

## 十、参考文献

### 核心论文
1. Xu, R., & Yan, Y. (2026). Agent Skills for Large Language Models: Architecture, Acquisition, Security, and the Path Forward. arXiv:2602.12430. https://arxiv.org/abs/2602.12430

2. Yue, L., et al. (2026). From Static Templates to Dynamic Runtime Graphs: A Survey of Workflow Optimization for LLM Agents. arXiv:2603.22386. https://arxiv.org/abs/2603.22386

3. Cheng, Y., et al. (2025). HAWK: A Hierarchical Workflow Framework for Multi-Agent Collaboration. arXiv:2507.04067. https://arxiv.org/abs/2507.04067

4. [The Meta-Agent Challenge] (2026). arXiv:2606.04455. https://arxiv.org/html/2606.04455v1

5. [AgentBench] (2024). ICLR 2026. https://arxiv.org/pdf/2308.03688

6. [Chain-of-Agents] (2024). Google Research. https://research.google/blog/chain-of-agents-large-language-models-collaborating-on-long-context-tasks/

7. [Graph of Agents] (2025). arXiv:2509.21848. https://arxiv.org/html/2509.21848v1

8. [Designing LLM-based Multi-Agent Systems for Software Engineering] (2025). arXiv:2511.08475. https://arxiv.org/html/2511.08475v1

9. [An LLM-Based Approach to Supporting Software Engineering Tasks] (2025). CMU-CS-25-132. http://ra.adm.cs.cmu.edu/anon/2025/CMU-CS-25-132.pdf

### 官方文档
10. LangChain. Workflows and Agents. https://docs.langchain.com/oss/python/langgraph/workflows-agents

11. Anthropic. Effective Context Engineering for AI Agents. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

### Benchmark 资源
12. SWE-bench. https://www.swebench.com/

13. OpenAI. Introducing SWE-bench Verified. https://openai.com/index/introducing-swe-bench-verified/

### 框架与工具
14. LangGraph. https://www.langchain.com/langgraph

15. Opik Agent Optimizer. https://www.comet.com/site/blog/automated-prompt-engineering/

---

**报告生成**: 2025-06-17
**数据源**: arXiv, Google Scholar, NeurIPS, ICLR, GitHub
**文献数量**: 50+ 篇核心论文
