"""基于LangGraph的输出Agent节点。"""

import json
import logging
from typing import Dict, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template

from ..models.state import PatentExtractionState


logger = logging.getLogger(__name__)


class OutputAgentNode:
    """输出Agent节点。
    
    负责将问答结果格式化为指定格式的输出。
    """
    
    def __init__(self):
        """初始化输出Agent节点。"""
        # 初始化Jinja2模板引擎
        template_dir = Path(__file__).parent.parent / "templates"
        template_dir.mkdir(exist_ok=True)
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
        
        # 创建默认模板
        self._create_default_templates()
        
        logger.info("输出Agent节点初始化完成")
    
    def process(self, state: PatentExtractionState) -> PatentExtractionState:
        """处理输出格式化。
        
        Args:
            state: 当前工作流状态
            
        Returns:
            更新后的状态
        """
        logger.info(f"开始输出格式化，格式: {state['output_format']}")
        
        try:
            # 更新当前步骤
            state["current_step"] = "output_formatting"
            state["completed_steps"].append("output_formatting")
            
            # 生成Markdown输出
            markdown_output = ""
            if state["output_format"] in ["markdown", "both"]:
                markdown_output = self._generate_markdown_output(state)
            
            # 生成JSON输出
            json_output = ""
            if state["output_format"] in ["json", "both"]:
                json_output = self._generate_json_output(state)
            
            # 更新状态
            state["markdown_output"] = markdown_output
            state["json_output"] = json_output
            state["next_step"] = END
            
            logger.info("输出格式化完成")
            return state
            
        except Exception as e:
            logger.error(f"输出格式化失败: {e}")
            state["error_message"] = str(e)
            state["next_step"] = END
            return state
    
    def _generate_markdown_output(self, state: PatentExtractionState) -> str:
        """生成Markdown格式输出。
        
        Args:
            state: 当前状态
            
        Returns:
            Markdown格式的字符串
        """
        template_path = state.get("template_path")
        
        if template_path and Path(template_path).exists():
            template = self._load_custom_template(template_path)
        else:
            template = self.jinja_env.get_template("default_markdown.md")
        
        return template.render(**state)
    
    def _generate_json_output(self, state: PatentExtractionState) -> str:
        """生成JSON格式输出。
        
        Args:
            state: 当前状态
            
        Returns:
            JSON格式的字符串
        """
        template_path = state.get("template_path")
        
        if template_path and Path(template_path).exists():
            template = self._load_custom_template(template_path)
        else:
            template = self.jinja_env.get_template("default_json.json")
        
        formatted_data = template.render(**state)
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
    
    def _create_default_templates(self) -> None:
        """创建默认模板文件。"""
        template_dir = Path(__file__).parent.parent / "templates"
        
        # 创建Markdown模板
        markdown_template = """# 专利信息提取结果

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

## 处理信息
- 处理时间: {{ processing_time }}s
- 使用模型: {{ model_used }}
- Token使用: {{ tokens_used }}

---
*生成时间: {{ completed_steps[-1] if completed_steps else 'unknown' }}*
"""
        
        markdown_file = template_dir / "default_markdown.md"
        markdown_file.write_text(markdown_template, encoding='utf-8')
        
        # 创建JSON模板
        json_template = """{
    "question": "{{ question }}",
    "answer": "{{ answer }}",
    "confidence_score": {{ confidence_score }},
    "relevant_sections": {{ relevant_sections | tojson }},
    "source_citations": {{ source_citations | tojson }},
    "processing_time": {{ processing_time }},
    "model_used": "{{ model_used }}",
    "tokens_used": {{ tokens_used }},
    "extracted_images": {{ extracted_images | tojson }},
    "image_descriptions": {{ image_descriptions | tojson }}
}"""
        
        json_file = template_dir / "default_json.json"
        json_file.write_text(json_template, encoding='utf-8')
