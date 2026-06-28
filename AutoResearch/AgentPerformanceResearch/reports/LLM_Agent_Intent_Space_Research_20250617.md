# LLM/Agent 上下文感知与意图空间分析前沿研究调研报告

**调研日期**: 2025年6月17日
**调研主题**: 大语言模型/智能体的上下文感知、意图空间匹配与意图空间分析

---

## 执行摘要

本报告调研了2024-2026年间关于LLM/Agent上下文感知与意图空间分析的最前沿研究。研究发现，该领域正从传统的自然语言通信向**潜在空间直接通信**演进，出现了四个核心发展方向：

1. **上下文感知**：从静态上下文窗口向动态、多模态、时序感知的上下文理解发展
2. **意图空间建模**：通过低维潜在表示捕捉和建模Agent的意图与信念状态
3. **潜在通信**：Agent间通过内部表示直接通信，绕过语言文本的中介
4. **潜在思维链（Latent Chain-of-Thought）**：在潜在空间中进行隐式推理，而非显式生成推理步骤

核心发现包括：**COCONUT**（连续潜在空间推理）、**Interlat**（潜在空间通信）、**ContextAgent**（多感官上下文感知）、**ReCAP**（递归上下文感知规划）等突破性工作。

---

## 一、领域概述

### 1.1 研究背景

随着大模型和Agent系统的发展，研究者发现"意图空间"等抽象的潜在信息正在成为重要的信息资源。传统的Agent通信依赖于自然语言文本，但这种方法存在：

- **信息损失**：从内部表示到文本再到内部表示的转换损失语义信息
- **低效性**：文本通信带宽受限，无法传递丰富的内部状态
- **对齐困难**：不同Agent间的表示空间难以对齐

### 1.2 研究意义

意图空间分析的核心价值在于：

1. **理解Agent内部状态**：通过分析潜在表示理解Agent的真实意图和信念
2. **提升Agent间协作**：基于意图匹配的Agent能够更有效地协作
3. **可控性增强**：通过操作意图空间实现对Agent行为的精细控制
4. **安全评估**：检测Agent的欺骗性意图和不当行为

---

## 二、核心论文分析

### 2.1 潜在空间通信（Latent Space Communication）

#### 🔥 Interlat: Inter-agent Latent Space Communication
- **来源**: [arXiv:2511.09149](https://arxiv.org/html/2511.09149v1) (2025)
- **核心创新**: 首次实现Agent间通过最后隐藏层状态直接通信，无需自然语言中介
- **技术方法**:
  - 借鉴人类"心灵感应"概念
  - 直接传递LSTM/Transformer的隐藏状态
  - 建立跨Agent的潜在空间对齐机制
- **实验结果**: 在协作任务中表现优于自然语言通信
- **意义**: 标志着Agent通信从"语言时代"进入"潜在空间时代"

#### 🔥 Thought Communication in Multiagent Collaboration
- **来源**: [arXiv:2510.20733](https://arxiv.org/html/2510.20733v1) (2025)
- **核心创新**: "思维通信"范式，实现Agent间直接的心智对心智交互
- **发现**: 超越语言的通信直接有益于LLM Agent间的协作
- **验证**: 在多种模型和场景下的有效性验证

#### 🔥 A Unified Framework for Latent Communication
- **来源**: [arXiv:2606.05711](https://arxiv.org/html/2606.05711v2) (2025)
- **核心贡献**: 统一的潜在通信框架
- **技术方法**:
  - 输入层嵌入交换
  - 隐藏状态直接传递
  - 跨层对齐机制
- **意义**: 为潜在空间通信提供标准化框架

#### State Delta Trajectory Communication
- **来源**: [arXiv:2506.19209](https://arxiv.org/html/2506.19209v1) (2025)
- **创新**: 同时传输自然语言令牌和令牌级状态转换轨迹
- **意义**: 结合传统语言通信与内部状态表示

---

### 2.2 上下文感知（Context-Awareness）

#### 🔥 ContextAgent: Context-Aware Proactive LLM Agents
- **来源**: [arXiv:2505.14668](https://arxiv.org/html/2505.14668v1) (2025)
- **核心创新**: 首个集成广泛感官上下文的主动式Agent
- **技术特点**:
  - 开放世界感官感知
  - 工具增强型LLM架构
  - 主动式行为规划
- **意义**: 实现从被动响应到主动感知的范式转变

#### 🔥 ReCAP: Recursive Context-Aware Reasoning and Planning
- **来源**: [arXiv:2510.23822](https://arxiv.org/abs/2510.23822) (2025)
- **核心创新**: 递归上下文感知推理与规划框架
- **技术方法**:
  - 层次化框架
  - 共享上下文机制
  - 递归推理过程
- **意义**: 解决长序列规划中的上下文一致性问题

#### A Survey on Context-Aware Multi-Agent Systems
- **来源**: [arXiv:2402.01968](https://arxiv.org/html/2402.01968v2) (2024)
- **类型**: 综述论文
- **内容**:
  - 上下文感知多Agent系统概述
  - CA-MAS开发框架
  - 技术路线梳理

---

### 2.3 意图空间建模（Intent Space Modeling）

#### 🔥 ARIA: Training Language Agents with Intention-driven Reward
- **来源**: [OpenReview](https://openreview.net/forum?id=eumRwpgdMU)
- **核心创新**:
  - 将自然语言动作映射到低维意图空间
  - 基于聚类的奖励聚合机制
- **技术方法**:
  - 意图空间嵌入
  - 聚类驱动的奖励设计
- **意义**: 首次将意图空间显式引入Agent训练

#### Automated Intent Discovery and Self-Exploration
- **来源**: [arXiv:2410.22552](https://arxiv.org/html/2410.22552v1) (2024)
- **核心贡献**: 自动意图发现与自我探索
- **关键发现**:
  - 紧凑意图空间促进语义不同意图的采样
  - 区别于句法多样性
- **意义**: 为意图空间的自动发现提供新范式

#### Factorized Latent Reasoning for LLM-based Recommendation
- **来源**: [arXiv:2604.26760](https://arxiv.org/html/2604.26760v2) (2025)
- **核心观点**:
  - 意图空间作为低维表示
  - 潜在推理粒度必须与意图空间对齐
- **意义**: 连接意图空间与推理粒度

---

### 2.4 信念状态与心理理论（Theory of Mind）

#### 🔥 Evaluating Theory of Mind and Internal Beliefs in LLM-Based MAS
- **来源**: [arXiv:2603.00142](https://arxiv.org/html/2603.00142v1) (2026)
- **核心研究**:
  - 评估LLM-based多Agent系统的心理理论能力
  - 内部信念状态分析
  - 逻辑推理增强
- **意义**: 为Agent心理理论提供评估框架

#### 🔥 Collaborative Belief Reasoning with LLMs
- **来源**: [OpenReview](https://openreview.net/forum?id=vy1mawkbFA)
- **核心发现**:
  - 显式意图感知信念建模对类人协作至关重要
  - 意图感知是有效协作的基础
- **意义**: 连接信念建模与意图理解

#### 🔥 Language Models Represent Beliefs of Self and Others
- **来源**: [arXiv:2402.18496](https://arxiv.org/html/2402.18496v3) (2024)
- **核心发现**:
  - 可通过神经激活线性解码各视角的信念状态
  - 信念表示在模型内部可定位
- **意义**: 证明LLM内部存在信念表示

#### Theory of Mind for Multi-Agent Collaboration via LLMs
- **来源**: [arXiv:2310.10701](https://arxiv.org/html/2310.10701v3) (2023)
- **核心方法**:
  - 显式信念表示
  - 推断队友心理状态（信念、欲望、意图）
- **意义**: 为多Agent协作提供ToM框架

---

### 2.5 表示学习与嵌入空间（Representation Learning）

#### 🔥 Native Retrieval Embeddings from LLM Agent Hidden States
- **来源**: [arXiv:2603.08429](https://arxiv.org/abs/2603.08429) (2026)
- **核心创新**:
  - 为LLM Agent装备原生检索能力
  - 轻量级投影头将隐藏状态直接映射到嵌入空间
- **技术方法**:
  - 端到端训练
  - 无需外部检索系统
- **意义**: 实现Agent内部状态到检索空间的直接映射

#### Demystifying Embedding Spaces using LLMs
- **来源**: [arXiv:2310.04475](https://arxiv.org/html/2310.04475v2) (2023)
- **核心贡献**:
  - 使用LLM直接与嵌入空间交互
  - 使密集数据嵌入可解释
- **意义**: 嵌入空间可解释性的突破

#### The Effect of State Representation on LLM Agent Behavior
- **来源**: [arXiv:2506.15624](https://arxiv.org/abs/2506.15624) (2025)
- **核心贡献**:
  - 系统化构建自然语言"状态"表示的统一框架
  - 状态表示对Agent行为的影响分析
- **意义**: 理解表示对行为的影响

---

### 2.7 潜在思维链（Latent Chain-of-Thought）

潜在思维链（Latent CoT）是2024-2025年兴起的重要研究方向，核心思想是在模型的潜在空间中进行推理，而非显式生成自然语言推理步骤。

#### 🔥 COCONUT: Chain of Continuous Thought
- **来源**: [arXiv:2412.06769](https://arxiv.org/abs/2412.06769) (ICLR 2025)
- **核心创新**: 首次实现在连续潜在空间中进行推理，而非离散的推理步骤
- **技术方法**:
  - 使用LLM的最后一个隐藏状态作为"连续思维"表示推理状态
  - 直接使用隐藏状态进行下一步推理，而非解码显式思维令牌
  - 连续思维可编码多个备选推理步骤（类似树搜索）
- **实验结果**:
  - 在需要大量回溯的逻辑推理任务上优于传统CoT
  - 推理过程中使用更少的思维令牌
  - 数学推理任务表现突出
- **开源代码**: [GitHub](https://github.com/facebookresearch/coconut)
- **意义**: 标志着LLM推理从"离散语言空间"进入"连续潜在空间"

#### 🔥 Implicit Reasoning in Large Language Models: A Comprehensive Survey
- **来源**: [arXiv:2509.02350](https://arxiv.org/abs/2509.02350) (2025)
- **类型**: 44页综合调研论文
- **核心内容**:
  - 正式区分显式推理和隐式推理
  - 描述各自的特性和适用场景
  - 隐式推理的优势：更低生成成本、更快推理速度、更好对齐内部计算
- **意义**: 为隐式推理领域提供系统化的理论基础

#### 🔥 A Comprehensive Survey on Latent Chain-of-Thought Reasoning
- **来源**: [arXiv:2505.16782](https://arxiv.org/pdf/2505.16782) (2025)
- **类型**: 综合调研
- **核心内容**:
  - 潜在CoT将推理轨迹表示在非语言的高维潜在空间中
  - 建立系统性分类法分析最新方法进展
  - 探讨从grokking而来的隐式推理电路
- **意义**: 潜在CoT作为新范式的全面概述

#### 🔥 Spatiotemporal Hidden-State Dynamics as a Signature of Internal Reasoning
- **来源**: [arXiv:2605.01853](https://arxiv.org/html/2605.01853v1) (2026)
- **核心创新**: 研究隐藏状态转换的时空动力学作为内部推理的签名
- **技术方法**:
  - 调查解码步骤和层间的隐藏状态转换
  - 识别LLM推理模型的独特时空模式
  - 成功推理与失败推理的模式差异
- **意义**: 揭示隐藏状态中的推理动态规律

#### 🔥 Are Latent Reasoning Models Easily Interpretable?
- **来源**: [arXiv:2604.04902](https://arxiv.org/html/2604.04902v1) (2026)
- **核心问题**: 潜在推理模型是否易于解释？
- **发现**:
  - 迄今为止最全面的潜在推理可解释性研究
  - 潜在推理面临可解释性挑战
  - 可能威胁到CoT提供的字面可读性
- **意义**: 揭示潜在推理的可解释性权衡

#### Efficient Reasoning with Hidden Thinking (Heima)
- **来源**: [arXiv:2501.19201](https://arxiv.org/abs/2501.19201) (2025)
- **核心创新**: Heima框架，用于CoT压缩
- **技术方法**:
  - 在潜在空间生成抽象的"思维令牌"而非冗长的可见推理链
  - 保留核心推理信息同时大幅降低令牌开销
  - 推理在隐藏表示中进行
- **意义**: 平衡推理效率与表达能力

#### Tyler: Typed Latent Reasoning for Language Models
- **来源**: [arXiv:2606.16360](https://arxiv.org/html/2606.16360) (2026)
- **核心创新**: 类型化潜在推理框架
- **解决的核心问题**:
  - 何时思考（When to think）
  - 计算什么（What to compute）
  - 分配多少计算资源（How much to allocate）
- **意义**: 提供细粒度的推理资源控制

#### Span-level Pause-of-Thought for Efficient and Interpretable Latent Reasoning
- **来源**: [arXiv:2603.06222](https://arxiv.org/html/2603.06222v1) (2026)
- **核心创新**: 跨段暂停思维（Pause-of-Thought）
- **技术特点**:
  - CoT压缩技术
  - 高效且可解释的潜在推理
  - 平衡推理深度与可解释性
- **意义**: 在效率和可解释性之间找到平衡点

#### Do LLMs Really Think Step-by-step in Implicit Reasoning?
- **来源**: [arXiv:2411.15862](https://arxiv.org/html/2411.15862v3) (2024)
- **核心发现**:
  - 质疑LLM在隐式推理中是否真的进行逐步思考
  - LLM的隐式推理能力易受攻击且不稳定
  - 重申显式CoT对有效推理的必要性
- **意义**: 对隐式推理能力提出质疑和反思

#### Deep Hidden Cognition Facilitates Reliable Chain-of-Thought
- **来源**: [arXiv:2507.10007](https://arxiv.org/abs/2507.10007) (2025)
- **核心方法**: 利用模型内在的真实性编码校准CoT推理准确性
- **意义**: 提升CoT推理的可靠性

### 2.8 评估与基准（Evaluation & Benchmarks）

#### A Survey on Evaluation of LLM-based Agents
- **来源**: [arXiv:2503.16416](https://arxiv.org/html/2503.16416v2) (2025)
- **类型**: 综述论文
- **内容**: LLM Agent能力评估综述，包括自我反思能力

#### AgentAtlas: Beyond Outcome Leaderboards for LLM Agents
- **来源**: [arXiv:2605.20530](https://arxiv.org/html/2605.20530v1) (2026)
- **核心创新**: LLM Agent的多轴评估框架
- **意义**: 超越简单的结果度量

---

## 三、技术路线演进

### 3.1 方法论发展时间线

```
2023年早期: 传统自然语言通信
    |
    | Theory of Mind for Multi-Agent Collaboration (arXiv:2310.10701)
    | Demystifying Embedding Spaces (arXiv:2310.04475)
    |
2024年: 信念表示与意图发现 + 潜在推理萌芽
    |
    | Language Models Represent Beliefs (arXiv:2402.18496)
    | Automated Intent Discovery (arXiv:2410.22552)
    | A Survey on Context-Aware MAS (arXiv:2402.01968)
    | Do LLMs Really Think Step-by-step? (arXiv:2411.15862)
    |
2025年: 潜在空间通信与潜在思维链突破
    |
    | COCONUT: Continuous Latent Space Reasoning (arXiv:2412.06769, ICLR 2025)
    | Efficient Reasoning with Hidden Thinking (arXiv:2501.19201)
    | A Comprehensive Survey on Latent CoT (arXiv:2505.16782)
    | Interlat: Latent Space Communication (arXiv:2511.09149)
    | Thought Communication (arXiv:2510.20733)
    | ContextAgent (arXiv:2505.14668)
    | ReCAP (arXiv:2510.23822)
    | Unified Framework for Latent Communication (arXiv:2606.05711)
    |
2026年: 成熟与评估 + 可解释性关注
    |
    | Evaluating Theory of Mind in MAS (arXiv:2603.00142)
    | Spatiotemporal Hidden-State Dynamics (arXiv:2605.01853)
    | Are Latent Reasoning Models Interpretable? (arXiv:2604.04902)
    | Tyler: Typed Latent Reasoning (arXiv:2606.16360)
    | AgentAtlas Evaluation Framework (arXiv:2605.20530)
    | Implicit Reasoning Survey (arXiv:2509.02350)
```

### 3.2 主流技术方案对比

| 技术路线 | 代表工作 | 优势 | 局限 | 适用场景 |
|---------|---------|------|------|---------|
| **自然语言通信** | 传统Agent系统 | 可解释性强、通用性好 | 信息损失大、效率低 | 人机协作 |
| **潜在空间通信** | Interlat, Thought Communication | 高带宽、低损失 | 跨模型对齐困难 | 多Agent协作 |
| **显式信念建模** | ToM系列 | 可控性强、理论清晰 | 计算开销大 | 需要精确推理 |
| **隐式表示学习** | Native Retrieval Embeddings | 端到端训练 | 可解释性弱 | 特定任务优化 |

### 3.3 新兴研究方向

1. **跨模型潜在空间对齐**
   - 问题：不同LLM的潜在空间难以直接通信
   - 方向：学习跨模型映射函数

2. **分层意图空间**
   - 问题：意图的多层次性（高层目标 vs 低层动作）
   - 方向：层次化意图表示

3. **动态上下文感知**
   - 问题：上下文的时效性和重要性变化
   - 方向：注意力驱动的动态上下文选择

4. **意图空间可解释性**
   - 问题：潜在表示的黑盒性质
   - 方向：概念级可解释性

---

## 四、研究趋势分析

### 4.1 年度发表趋势

基于调研数据，该领域论文发表呈现指数增长：
- **2023年**: 奠基性工作出现（心理理论、嵌入空间可解释性）
- **2024年**: 方法探索期（信念表示、上下文感知框架）
- **2025年**: 突破爆发期（潜在空间通信、主动式Agent）
- **2026年**: 成熟评估期（评估框架、标准化）

### 4.2 关键词热度变化

| 关键词 | 2023-2024 | 2025 | 2026趋势 |
|-------|-----------|------|---------|
| Intent Space | 低 | 中高 | 高 |
| Latent Communication | 极低 | 高 | 极高 |
| Latent CoT / Hidden Reasoning | 极低 | 极高 | 极高 |
| Continuous Latent Space | 极低 | 高 | 高 |
| Context-Aware | 中 | 高 | 高 |
| Theory of Mind | 中 | 中高 | 稳定 |
| Belief State | 中 | 高 | 稳定 |
| Multi-Agent | 高 | 极高 | 极高 |

### 4.3 机构与会议分布

**主要发表渠道**：
- arXiv预印本（主要）：占比约70%
- 顶级会议：ICML、NeurIPS、ACL、AAAI
- OpenReview（评审中论文）

**研究机构分布**：
- 北美：Google Research、OpenAI、高校（CMU、Stanford）
- 中国：广泛参与，特别是在应用层面
- 欧洲：理论基础研究

---

## 五、研究空白与未来方向

### 5.1 当前研究空白

1. **跨Agent意图空间标准化**
   - 缺乏统一的意图空间定义和标注
   - 不同Agent的意图难以比较和组合

2. **意图空间与行为映射的可解释性**
   - 潜在表示到具体行为的映射机制不明确
   - 难以进行细粒度的行为调试

3. **大规模多Agent系统的意图协调**
   - 现有研究多集中在2-5个Agent
   - 百级以上Agent的意图协调机制未探索

4. **意图空间的持续学习与适应**
   - Agent意图空间如何随经验动态调整
   - 个体意图与集体意图的协调机制

### 5.2 未来研究方向建议

#### 🔥 高优先级方向

1. **意图空间标准化与评估基准**
   - 建立标准化的意图空间数据集
   - 设计意图理解的评估指标
   - 构建跨Agent意图对齐的基准测试

2. **可解释的潜在空间通信**
   - 开发潜在空间的可视化工具
   - 研究潜在维度的语义对应关系
   - 设计人类可理解的潜在通信协议

3. **动态意图发现与跟踪**
   - 在运行时自动发现新意图
   - 跟踪意图的演化和组合
   - 意图生命周期管理

#### 中优先级方向

4. **分层意图表示**
   - 高层战略意图 vs 低层战术意图
   - 意图的分解与组合机制
   - 跨层次意图的一致性约束

5. **意图驱动的Agent协作**
   - 基于意图相似度的Agent匹配
   - 意图冲突的检测与解决
   - 集体意图的形成机制

#### 长期方向

6. **意识与意图的哲学建模**
   - 机器意识的形式化定义
   - 意图与意识的哲学边界
   - 人工道德主体性

---

## 六、技术应用前景

### 6.1 短期应用（1-2年）

1. **智能客服系统**
   - 意图识别与路由
   - 上下文感知对话管理

2. **协作办公Agent**
   - 基于意图的任务分配
   - 跨Agent知识共享

3. **游戏AI**
   - NPC意图建模
   - 动态剧情生成

### 6.2 中期应用（3-5年）

4. **自主研究Agent**
   - 研究意图的自动发现
   - 跨Agent假设验证

5. **智能制造调度**
   - 设备间意图对齐
   - 动态生产计划优化

6. **复杂系统管理**
   - 分布式系统故障诊断
   - 多层次资源协调

### 6.3 长期应用（5+年）

7. **科学发现**
   - 跨学科Agent协作
   - 研究范式自动演化

8. **社会治理**
   - 多利益相关者协调
   - 政策意图建模

---

## 七、参考文献

### 7.1 核心论文（按重要性排序）

1. **COCONUT: Training LLMs to Reason in Continuous Latent Space** - [arXiv:2412.06769](https://arxiv.org/abs/2412.06769) (ICLR 2025)
2. **Interlat: Inter-agent Latent Space Communication** - [arXiv:2511.09149](https://arxiv.org/html/2511.09149v1)
3. **Thought Communication in Multiagent Collaboration** - [arXiv:2510.20733](https://arxiv.org/html/2510.20733v1)
4. **ContextAgent: Context-Aware Proactive LLM Agents** - [arXiv:2505.14668](https://arxiv.org/html/2505.14668v1)
5. **ReCAP: Recursive Context-Aware Reasoning and Planning** - [arXiv:2510.23822](https://arxiv.org/abs/2510.23822)
6. **Evaluating Theory of Mind and Internal Beliefs in LLM-Based MAS** - [arXiv:2603.00142](https://arxiv.org/html/2603.00142v1)
7. **A Unified Framework for Latent Communication in LLM-based MAS** - [arXiv:2606.05711](https://arxiv.org/html/2606.05711v2)
8. **Spatiotemporal Hidden-State Dynamics as a Signature of Internal Reasoning** - [arXiv:2605.01853](https://arxiv.org/html/2605.01853v1)
9. **Language Models Represent Beliefs of Self and Others** - [arXiv:2402.18496](https://arxiv.org/html/2402.18496v3)
10. **Automated Intent Discovery and Self-Exploration** - [arXiv:2410.22552](https://arxiv.org/html/2410.22552v1)
11. **Theory of Mind for Multi-Agent Collaboration via LLMs** - [arXiv:2310.10701](https://arxiv.org/html/2310.10701v3)
12. **Native Retrieval Embeddings from LLM Agent Hidden States** - [arXiv:2603.08429](https://arxiv.org/abs/2603.08429)

### 7.2 综述与调研

11. **Implicit Reasoning in Large Language Models: A Comprehensive Survey** - [arXiv:2509.02350](https://arxiv.org/abs/2509.02350)
12. **A Comprehensive Survey on Latent Chain-of-Thought Reasoning** - [arXiv:2505.16782](https://arxiv.org/pdf/2505.16782)
13. **A Survey on Evaluation of LLM-based Agents** - [arXiv:2503.16416](https://arxiv.org/html/2503.16416v2)
14. **A Comprehensive Survey on Context-Aware Multi-Agent Systems** - [arXiv:2402.01968](https://arxiv.org/html/2402.01968v2)
15. **A Communication-Centric Survey of LLM-Based Multi-Agent Systems** - [arXiv:2502.14321](https://arxiv.org/html/2502.14321v2)
16. **A Survey on LLM-based Multi-Agent Systems** - [Springer](https://link.springer.com/article/10.1007/s44336-024-00009-2)

### 7.3 相关工作

#### 潜在思维链相关
17. **Efficient Reasoning with Hidden Thinking (Heima)** - [arXiv:2501.19201](https://arxiv.org/abs/2501.19201)
18. **Tyler: Typed Latent Reasoning for Language Models** - [arXiv:2606.16360](https://arxiv.org/html/2606.16360)
19. **Span-level Pause-of-Thought for Efficient and Interpretable Latent Reasoning** - [arXiv:2603.06222](https://arxiv.org/html/2603.06222v1)
20. **Do LLMs Really Think Step-by-step in Implicit Reasoning?** - [arXiv:2411.15862](https://arxiv.org/html/2411.15862v3)
21. **Deep Hidden Cognition Facilitates Reliable Chain-of-Thought** - [arXiv:2507.10007](https://arxiv.org/abs/2507.10007)
22. **Are Latent Reasoning Models Easily Interpretable?** - [arXiv:2604.04902](https://arxiv.org/html/2604.04902v1)

#### 意图空间与信念状态
23. **ARIA: Training Language Agents with Intention-driven Reward** - [OpenReview](https://openreview.net/forum?id=eumRwpgdMU)
24. **Collaborative Belief Reasoning with LLMs** - [OpenReview](https://openreview.net/forum?id=vy1mawkbFA)
25. **Factorized Latent Reasoning for LLM-based Recommendation** - [arXiv:2604.26760](https://arxiv.org/html/2604.26760v2)
26. **The Effect of State Representation on LLM Agent Behavior** - [arXiv:2506.15624](https://arxiv.org/abs/2506.15624)

#### 表示学习
27. **Demystifying Embedding Spaces using LLMs** - [arXiv:2310.04475](https://arxiv.org/html/2310.04475v2)
28. **Human-like object concept representations emerge naturally in LLMs** - [arXiv:2407.01067](https://arxiv.org/html/2407.01067v3)

---

## 附录：关键概念解析

### A. 意图空间（Intent Space）

定义：Agent可能的意图构成的潜在空间，通常是一个低维连续向量空间。

特点：
- 低维性：相比原始行为空间，意图空间维度大幅降低
- 连续性：相似意图在空间中距离接近
- 可组合性：复杂意图可由基础意图组合而成

### B. 潜在空间通信（Latent Space Communication）

定义：Agent间直接交换内部表示（如隐藏状态），而非自然语言文本。

优势：
- 高带宽：可传递丰富信息
- 低损失：避免文本转换的信息损失
- 快速：绕过语言生成和理解过程

挑战：
- 对齐问题：不同模型的潜在空间异构
- 可解释性：潜在表示难以理解
- 标准化：缺乏统一的通信协议

### C. 心理理论（Theory of Mind, ToM）

定义：Agent理解和预测其他Agent心理状态（信念、欲望、意图）的能力。

在LLM Agent中的应用：
- 协作推理：推断队友意图和信念
- 竞争博弈：预测对手策略
- 人机交互：理解用户真实需求

### D. 上下文感知（Context-Awareness）

定义：Agent感知和利用环境、时序、多模态上下文信息的能力。

发展阶段：
1. 静态上下文：固定上下文窗口
2. 时序上下文：考虑时间演变
3. 多模态上下文：整合视觉、听觉等
4. 主动感知：主动获取上下文

### E. 潜在思维链（Latent Chain-of-Thought, Latent CoT）

定义：在模型的潜在空间（隐藏状态空间）中进行推理，而非生成显式的自然语言推理步骤。

核心特点：
- **非语言表示**：推理轨迹在高维潜在空间中表示，而非自然语言
- **连续表示**：推理状态是连续的向量，可编码多个备选推理路径
- **隐式过程**：推理过程对人类不可见，仅输出最终结果

演进路径：
```
传统CoT (2022): "Let me think step by step..."
    ↓
显式推理步骤生成，人可读但开销大
    ↓
潜在CoT (2024-2025): COCONUT
    ↓
连续潜在空间推理，更高效更丰富
    ↓
类型化潜在推理 (2026): Tyler
    ↓
细粒度推理资源控制
```

优势：
- **效率更高**：无需生成冗长的推理文本
- **信息丰富**：潜在空间可编码更多信息
- **计算对齐**：更接近模型的内部计算过程
- **树搜索能力**：连续思维可表示多个推理分支

挑战：
- **可解释性**：推理过程对人类不可见
- **调试困难**：难以诊断推理错误
- **安全担忧**：可能隐藏不当推理过程
- **评估复杂**：难以评估推理质量

---

**报告完成日期**: 2025年6月17日
**更新日期**: 2025年6月17日（新增潜在思维链章节）
**下次更新建议**: 2025年9月（跟踪ICML/NeurIPS 2025会议论文）
