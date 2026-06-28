"""
报告生成模块
生成格式化的研究报告
"""
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from .config import Config
from . import RESEARCH_TEMPLATES
from .researcher import ResearchResult


class ReportGenerator:
    """报告生成器"""

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Config.REPORTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_single_report(
        self,
        result: ResearchResult,
        research_type: str = "通用"
    ) -> str:
        """生成单次研究的报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self._sanitize_filename(result.topic)}_研究报告_{timestamp}.md"
        filepath = self.output_dir / filename

        template = RESEARCH_TEMPLATES.get(research_type, RESEARCH_TEMPLATES["通用"])

        report = self._build_report_template(result.topic, research_type, template)
        report += self._format_content(result.content)
        report += self._build_footer(result)

        filepath.write_text(report, encoding="utf-8")

        return str(filepath)

    def generate_comprehensive_report(
        self,
        topic: str,
        results: List[ResearchResult],
        research_type: str = "通用",
        aspects: List[str] = None
    ) -> str:
        """生成综合研究报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self._sanitize_filename(topic)}_综合研究报告_{timestamp}.md"
        filepath = self.output_dir / filename

        template = RESEARCH_TEMPLATES.get(research_type, RESEARCH_TEMPLATES["通用"])

        report = self._build_comprehensive_header(topic, research_type, template)
        report += self._build_executive_summary(results)
        report += self._build_detailed_analysis(results, aspects)
        report += self._build_conclusions(results, aspects)
        report += self._build_comprehensive_footer(results)

        filepath.write_text(report, encoding="utf-8")

        return str(filepath)

    def generate_html_report(self, markdown_path: str) -> str:
        """生成 HTML 格式报告"""
        import subprocess

        try:
            # 尝试使用 pandoc 转换
            result = subprocess.run(
                ["pandoc", "-f", "markdown", "-t", "html", "-o",
                 markdown_path.replace(".md", ".html"), markdown_path],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return markdown_path.replace(".md", ".html")
            else:
                print(f"HTML 转换失败: {result.stderr}")
                return markdown_path

        except FileNotFoundError:
            print("未找到 pandoc，跳过 HTML 转换")
            return markdown_path

    def _sanitize_filename(self, name: str) -> str:
        """清理文件名"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, "_")
        return name[:50]  # 限制长度

    def _build_report_template(
        self,
        topic: str,
        research_type: str,
        template: Dict
    ) -> str:
        """构建报告头部模板"""
        return f"""# {topic} 研究报告

**研究类型**: {research_type}
**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**模型**: {Config.MODEL}

---

## 研究概述

{template['description']}

本研究重点关注：{', '.join(template['focus_areas'])}

---

"""

    def _build_comprehensive_header(
        self,
        topic: str,
        research_type: str,
        template: Dict
    ) -> str:
        """构建综合报告头部"""
        return f"""# {topic} 综合研究报告

**研究类型**: {research_type}
**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**模型**: {Config.MODEL}

---

## 📋 目录

1. [研究概述](#研究概述)
2. [执行摘要](#执行摘要)
3. [详细分析](#详细分析)
4. [研究结论](#研究结论)
5. [参考资料](#参考资料)

---

## 研究概述

{template['description']}

本研究重点关注：{', '.join(template['focus_areas'])}

---

"""

    def _format_content(self, content: str) -> str:
        """格式化内容"""
        return f"\n{content}\n"

    def _build_executive_summary(self, results: List[ResearchResult]) -> str:
        """构建执行摘要"""
        section = "## 执行摘要\n\n"

        # 汇总所有内容的关键点
        total_tokens = sum(r.token_usage.get("total_tokens", 0) for r in results)

        section += f"本研究包含 {len(results)} 个研究维度，"
        section += f"累计使用 {total_tokens} tokens 进行分析。\n\n"

        # 从第一个结果中提取关键信息
        if results:
            first_content = results[0].content
            # 尝试提取开头段落作为摘要
            lines = first_content.split("\n")
            summary_lines = []
            for line in lines[:10]:
                if line.strip():
                    summary_lines.append(line)
                if len(summary_lines) >= 3:
                    break

            section += "\n".join(summary_lines)

        section += "\n\n---\n\n"

        return section

    def _build_detailed_analysis(
        self,
        results: List[ResearchResult],
        aspects: List[str] = None
    ) -> str:
        """构建详细分析部分"""
        section = "## 详细分析\n\n"

        for i, result in enumerate(results, 1):
            aspect_title = aspects[i - 1] if aspects and i <= len(aspects) else f"研究维度 {i}"

            section += f"### {i}. {aspect_title}\n\n"
            section += result.content + "\n\n"

            if result.reasoning:
                section += f"<details>\n<summary>🧠 推理过程</summary>\n\n{result.reasoning}\n</details>\n\n"

            section += "---\n\n"

        return section

    def _build_conclusions(
        self,
        results: List[ResearchResult],
        aspects: List[str] = None
    ) -> str:
        """构建结论部分"""
        section = "## 研究结论\n\n"

        # 最后一个结果通常包含综合信息
        if results:
            last_result = results[-1]
            # 提取结论性内容
            content = last_result.content

            # 简单处理：取最后部分
            lines = content.split("\n")
            conclusion_lines = []
            for line in reversed(lines):
                if line.strip():
                    conclusion_lines.insert(0, line)
                if len(conclusion_lines) >= 5:
                    break

            if conclusion_lines:
                section += "\n".join(conclusion_lines)
            else:
                section += "基于以上研究分析，请参考详细分析部分的结论。"

        section += "\n\n---\n\n"

        return section

    def _build_footer(self, result: ResearchResult) -> str:
        """构建报告尾部"""
        footer = "---\n\n"
        footer += "## 研究元数据\n\n"

        if result.token_usage:
            usage = result.token_usage
            footer += f"- **Prompt Tokens**: {usage.get('prompt_tokens', 'N/A')}\n"
            footer += f"- **Completion Tokens**: {usage.get('completion_tokens', 'N/A')}\n"
            footer += f"- **Total Tokens**: {usage.get('total_tokens', 'N/A')}\n"
            if 'reasoning_tokens' in usage.get('completion_tokens_details', {}):
                rt = usage['completion_tokens_details']['reasoning_tokens']
                footer += f"- **Reasoning Tokens**: {rt}\n"

        footer += f"\n- **研究时间**: {result.timestamp}\n"
        footer += f"- **使用模型**: {Config.MODEL}\n"

        return footer

    def _build_comprehensive_footer(self, results: List[ResearchResult]) -> str:
        """构建综合报告尾部"""
        footer = "---\n\n## 研究元数据\n\n"

        total_prompt = sum(r.token_usage.get("prompt_tokens", 0) for r in results)
        total_completion = sum(r.token_usage.get("completion_tokens", 0) for r in results)
        total_reasoning = sum(
            r.token_usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
            for r in results
        )

        footer += f"- **研究维度数**: {len(results)}\n"
        footer += f"- **总 Prompt Tokens**: {total_prompt}\n"
        footer += f"- **总 Completion Tokens**: {total_completion}\n"
        footer += f"- **总 Reasoning Tokens**: {total_reasoning}\n"
        footer += f"- **总 Tokens**: {total_prompt + total_completion}\n"
        footer += f"\n- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        footer += f"- **使用模型**: {Config.MODEL}\n"

        footer += "\n---\n\n"
        footer += "*本报告由 AutoResearch 自动生成，建议结合人工审核使用。*"

        return footer


def print_report_summary(filepath: str):
    """打印报告摘要"""
    print("\n" + "=" * 60)
    print("📄 研究报告已生成")
    print("=" * 60)
    print(f"文件路径: {filepath}")
    print(f"文件大小: {os.path.getsize(filepath) / 1024:.1f} KB")
    print("=" * 60)
