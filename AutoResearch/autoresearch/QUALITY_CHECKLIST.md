# AutoResearch 质量检查清单

## 报告生成前检查

### 配置检查
- [ ] API Key 已配置且有效
- [ ] 输出目录可写
- [ ] WebSearch 功能可用

## 报告内容质量检查

### 执行摘要
- [ ] 包含研究目的说明
- [ ] 包含主要发现（3-5条）
- [ ] 包含研究范围和维度说明
- [ ] 包含来源数量统计

### 详细分析
- [ ] 每个维度有清晰的标题
- [ ] 内容结构化（使用子标题、列表）
- [ ] 包含具体数据和事实
- [ ] 包含对比分析（表格形式）
- [ ] 技术细节准确

### 来源引用
- [ ] 每篇论文包含 arXiv 编号
- [ ] 每个来源有完整链接
- [ ] 作者信息完整
- [ ] 发表年份标注
- [ ] GitHub 仓库链接（如适用）

### 参考文献部分
- [ ] 按重要性排序
- [ ] 分类清晰（论文/仓库/文档）
- [ ] 格式统一
- [ ] 链接有效

### 技术对比
- [ ] 包含对比表格
- [ ] 优势/局限性分析
- [ ] 适用场景说明

### 趋势分析
- [ ] 时间线清晰
- [ ] 关键词热度分析
- [ ] 机构/会议分布

### 实践建议
- [ ] 具体可操作
- [ ] 优先级明确
- [ ] 资源链接完整

### 元数据
- [ ] Token 使用统计
- [ ] 生成时间
- [ ] 模型版本
- [ ] WebSearch 状态

## 置信度检查

### 高置信度来源比例
- [ ] arXiv 论文占比 > 50%
- [ ] 官方文档/仓库占比 > 30%

### 来源时效性
- [ ] 大部分来源近3年内
- [ ] 包含最新进展（近6个月）

### 来源相关性
- [ ] 所有来源与研究主题相关
- [ ] 核心观点有可靠来源

## 格式检查

### Markdown 格式
- [ ] 标题层级正确
- [ ] 列表格式正确
- [ ] 表格对齐
- [ ] 代码块标记正确

### 可读性
- [ ] 无过长段落
- [ ] 空行适当
- [ ] 标点正确

## 自动化测试建议

```python
def check_report_quality(filepath: Path) -> Dict:
    """检查报告质量"""
    content = filepath.read_text()

    checks = {
        "has_arxiv_links": "arxiv.org/abs/" in content,
        "has_github_links": "github.com" in content,
        "has_references": "## 参考文献" in content,
        "has_executive_summary": "## 执行摘要" in content,
        "has_conclusions": "## 研究结论" in content or "## 结论" in content,
        "has_comparison": "| 维度 |" in content,
        "has_metadata": "Token" in content or "研究元数据" in content,
    }

    score = sum(checks.values()) / len(checks) * 100

    return {"score": score, "checks": checks}
```

## 持续改进

- 定期回顾报告质量
- 收集用户反馈
- 更新方法论
- 优化提示词
