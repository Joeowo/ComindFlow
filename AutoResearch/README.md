# AutoResearch

基于 DeepSeek V4-Pro + WebSearch 的智能自动化研究工具。

## 功能特点

### V1 版本（基础版）
- 🔍 **智能搜索**: 利用 DeepSeek 的 WebSearch 功能获取最新信息
- 📊 **多种研究模式**: 单次研究、深度研究、交互式研究
- 📝 **自动报告**: 生成结构化的 Markdown 研究报告
- 🎯 **专业模板**: 内置学术、技术、市场、产品等研究模板
- 🤖 **自然语言处理**: 自动分析用户需求，生成研究计划

### V2 版本（强化置信度）✨ 新增
- 📚 **学术规范性**: 完整的参考文献格式，符合学术标准
- 🔗 **来源可追溯**: 每个观点都有 arXiv 编号和链接
- 🎯 **置信度标注**: 区分高/中/低置信度来源
- 📊 **质量检查**: 内置质量检查清单
- 📖 **方法论文档**: 完整的研究方法论文档

## 安装

```bash
# 克隆项目
git clone <repo>
cd AutoResearch

# 安装依赖
pip install -r requirements.txt
```

## 配置

在项目根目录创建 `.env` 文件：

```env
apikey=sk-your-deepseek-api-key
base=https://api.deepseek.com
model=deepseek-v4-pro
```

## 使用方法

### V1 基础用法

```bash
# 单次研究
python -m autoresearch "RAG 技术调研"

# 深度研究（多维度）
python -m autoresearch "大模型微调" --mode deep --type 技术

# 自然语言模式（自动分析）
python -m autoresearch "帮我调研一下 Agent 技能和工作流优化的最新研究"
```

### V2 强化版（推荐）

```bash
# 使用 V2 版本（强化置信度）
python -m autoresearch_v2 "RAG 技术调研"

# V2 深度研究
python -m autoresearch_v2 "大模型微调" --mode deep --type 技术

# V2 自然语言模式
python -m autoresearch_v2 "帮我调研 Agent 技能和工作流优化的最新研究"
```

### 研究模式

| 模式 | 说明 | 参数 |
|------|------|------|
| auto | 智能分析，自动规划（默认） | `--mode auto` |
| single | 单次综合研究 | `--mode single` |
| deep | 多维度深度研究 | `--mode deep` |
| interactive | 交互式生成问题 | `--mode interactive` |

### 研究类型

```bash
# 查看所有研究类型
python -m autoresearch --list-types
```

可用类型：
- **学术**: 论文搜索、引用分析、文献综述
- **技术**: 技术调研、框架对比、发展趋势
- **市场**: 市场分析、竞争格局、趋势预测
- **产品**: 产品功能、用户评价、竞品分析
- **通用**: 综合信息搜集

## 输出

研究报告保存在 `output/reports/` 目录：

```
output/
└── reports/
    ├── 主题_研究报告_YYYYMMDD_HHMMSS.md
    └── 主题_综合研究报告_YYYYMMDD_HHMMSS.md
```

### V2 报告结构（增强版）

1. **研究概述** - 研究背景和重点
2. **执行摘要** - 关键发现和统计
3. **详细分析** - 分维度深入分析
4. **技术路线对比** - 对比表格
5. **研究趋势** - 时间线和趋势
6. **研究结论** - 总结性发现
7. **实践建议** - 可操作建议
8. **参考文献** - 完整引用列表
9. **研究元数据** - Token 使用、置信度说明

### V2 置信度体系

| 置信度 | 来源类型 | 说明 |
|--------|----------|------|
| 高 | arXiv 论文、官方文档、GitHub 仓库 | 可验证性高 |
| 中 | 技术博客、社区文档 | 需要交叉验证 |
| 低 | 未经验证的信息 | 谨慎使用 |

## 项目结构

```
AutoResearch/
├── .env                          # 配置文件
├── METHODOLOGY.md                # 研究方法论 ✨
├── QUALITY_CHECKLIST.md          # 质量检查清单 ✨
├── autoresearch/
│   ├── __init__.py              # 包初始化
│   ├── __main__.py              # 主入口
│   ├── config.py                # 配置管理
│   ├── planner.py               # 任务规划器
│   ├── researcher.py            # 核心研究模块 (V1)
│   ├── researcher_v2.py         # 核心研究模块 (V2) ✨
│   ├── reporter.py              # 报告生成 (V1)
│   ├── reporter_v2.py           # 报告生成 (V2) ✨
│   ├── utils.py                 # 工具函数
│   └── main.py                 # CLI 程序
│   └── main_v2.py              # CLI 程序 (V2) ✨
├── output/
│   └── reports/                 # 研究报告输出
├── requirements.txt             # 依赖
├── test_websearch.py           # WebSearch 测试
└── README.md                   # 本文件
```

## V1 vs V2 对比

| 特性 | V1 | V2 |
|------|-----|-----|
| 自然语言理解 | ✅ | ✅ |
| 自动规划 | ✅ | ✅ |
| WebSearch | ✅ | ✅ |
| 来源追踪 | ⚠️ 有限 | ✅ 完整 |
| 参考文献 | ⚠️ 简单 | ✅ 标准格式 |
| 置信度标注 | ❌ | ✅ |
| 质量检查 | ❌ | ✅ 清单 |
| 方法论文档 | ❌ | ✅ 完整 |

## 开发

### V1 基础版

```python
from autoresearch import DeepSeekResearcher, ReportGenerator, Config

Config.validate()
researcher = DeepSeekResearcher()
result = researcher.search("研究主题")
reporter = ReportGenerator()
filepath = reporter.generate_single_report(result)
```

### V2 强化版

```python
from autoresearch.researcher_v2 import DeepSeekResearcher, SearchQuery
from autoresearch.reporter_v2 import ReportGenerator
from autoresearch import Config

Config.validate()
researcher = DeepSeekResearcher()
query = SearchQuery(
    query="研究主题",
    depth="comprehensive",
    require_sources=True  # 要求提供来源
)
result = researcher.search(query)
reporter = ReportGenerator()
filepath = reporter.generate_single_report(result)

# 查看收集的来源
for source in result.sources:
    print(f"{source.title} - {source.url} (置信度: {source.confidence})")
```

## 质量保证

使用质量检查清单验证报告质量：

```python
from autoresearch import QUALITY_CHECKLIST_PATH
import subprocess

# 查看质量检查清单
with open(QUALITY_CHECKLIST_PATH) as f:
    print(f.read())
```

## 许可

MIT License
