"""输出Agent实现。

负责将问答结果格式化为Markdown和JSON输出。
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from jinja2 import Environment, FileSystemLoader, Template

from ..models.patent import PatentResult


logger = logging.getLogger(__name__)


class OutputAgent:
    """输出Agent。
    
    负责将问答结果格式化为用户指定的输出格式。
    """
    
    def __init__(self) -> None:
        """初始化输出Agent。"""
        # 初始化Jinja2模板引擎
        template_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
        
        # 加载默认模板
        self.default_markdown_template = self._load_default_markdown_template()
        self.default_json_template = self._load_default_json_template()
        
        logger.info("输出Agent初始化完成")
    
    def format_output(
        self, 
        answer_result: Dict[str, Any], 
        output_format: str,
        template_path: Optional[str] = None
    ) -> PatentResult:
        """格式化输出结果。
        
        Args:
            answer_result: 问答结果
            output_format: 输出格式 ("markdown", "json", "both")
            template_path: 自定义模板路径
            
        Returns:
            格式化的专利结果
        """
        logger.info(f"开始格式化输出，格式: {output_format}")
        
        try:
            # 生成Markdown输出
            markdown_output = ""
            if output_format in ["markdown", "both"]:
                markdown_output = self._generate_markdown_output(answer_result, template_path)
            
            # 生成JSON输出
            json_output = ""
            if output_format in ["json", "both"]:
                json_output = self._generate_json_output(answer_result, template_path)
            
            # 创建结果对象
            result = PatentResult(
                answer=answer_result["answer"],
                confidence_score=answer_result["confidence_score"],
                markdown_output=markdown_output,
                json_output=json_output,
                processing_time=0.0,  # TODO: 实际统计
                tokens_used=answer_result.get("tokens_used", 0),
                model_used=answer_result.get("model_used", "unknown"),
                relevant_sections=answer_result.get("relevant_sections", []),
                source_citations=answer_result.get("source_citations", []),
                extracted_images=[],  # TODO: 从answer_result中获取
                image_descriptions=[]  # TODO: 从answer_result中获取
            )
            
            logger.info("输出格式化完成")
            return result
            
        except Exception as e:
            logger.error(f"输出格式化失败: {e}")
            raise
    
    def _generate_markdown_output(self, answer_result: Dict[str, Any], template_path: Optional[str]) -> str:
        """生成Markdown格式输出。
        
        Args:
            answer_result: 问答结果
            template_path: 自定义模板路径
            
        Returns:
            Markdown格式的字符串
        """
        if template_path:
            template = self._load_custom_template(template_path)
        else:
            template = self.default_markdown_template
        
        return template.render(**answer_result)
    
    def _generate_json_output(self, answer_result: Dict[str, Any], template_path: Optional[str]) -> str:
        """生成JSON格式输出。
        
        Args:
            answer_result: 问答结果
            template_path: 自定义模板路径
            
        Returns:
            JSON格式的字符串
        """
        if template_path:
            template = self._load_custom_template(template_path)
        else:
            template = self.default_json_template
        
        formatted_data = template.render(**answer_result)
        return json.dumps(json.loads(formatted_data), ensure_ascii=False, indent=2)
    
    def _load_custom_template(self, template_path: str) -> Template:
        """加载自定义模板。
        
        Args:
            template_path: 模板文件路径
            
        Returns:
            Jinja2模板对象
        """
        template_file = Path(template_path)
        if not template_file.exists():
            raise FileNotFoundError(f"模板文件不存在: {template_path}")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        return Template(template_content)
    
    def _load_default_markdown_template(self) -> Template:
        """加载默认Markdown模板。"""
        template_content = """# 专利信息提取结果

## 问题
{{ question }}

## 答案
{{ answer }}

## 置信度
{{ confidence_score }}

## 相关文档片段
{% for section in relevant_sections %}
- {{ section }}
{% endfor %}

## 引用来源
{% for citation in source_citations %}
- {{ citation }}
{% endfor %}

---
*生成时间: {{ processing_time }}s | 使用模型: {{ model_used }} | Token使用: {{ tokens_used }}*
"""
        return Template(template_content)
    
    def _load_default_json_template(self) -> Template:
        """加载默认JSON模板。"""
        template_content = """{
    "question": "{{ question }}",
    "answer": "{{ answer }}",
    "confidence_score": {{ confidence_score }},
    "relevant_sections": {{ relevant_sections | tojson }},
    "source_citations": {{ source_citations | tojson }},
    "processing_time": {{ processing_time }},
    "model_used": "{{ model_used }}",
    "tokens_used": {{ tokens_used }}
}"""
        return Template(template_content)
