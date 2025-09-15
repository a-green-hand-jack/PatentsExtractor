"""专利相关数据模型定义。"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class PatentDocument:
    """专利文档数据模型。
    
    用于存储从PDF或网页中提取的专利信息。
    """
    
    # 基本信息
    title: str
    abstract: str
    inventors: List[str]
    assignee: str
    publication_number: str
    publication_date: datetime
    
    # 内容
    description: str
    claims: str
    drawings: List[str]  # 图片路径列表
    
    # 元数据
    source_type: str  # "pdf" 或 "web"
    source_path: str
    extraction_time: datetime
    
    # 结构化内容
    structured_content: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        return {
            "title": self.title,
            "abstract": self.abstract,
            "inventors": self.inventors,
            "assignee": self.assignee,
            "publication_number": self.publication_number,
            "publication_date": self.publication_date.isoformat(),
            "description": self.description,
            "claims": self.claims,
            "drawings": self.drawings,
            "source_type": self.source_type,
            "source_path": self.source_path,
            "extraction_time": self.extraction_time.isoformat(),
            "structured_content": self.structured_content,
        }


@dataclass
class PatentQuery:
    """专利查询请求数据模型。
    
    用于封装用户的查询请求和相关配置。
    """
    
    # 输入源
    input_source: str  # PDF文件路径或网页URL
    
    # 查询内容
    question: str
    context: Optional[str] = None  # 额外的上下文信息
    
    # 输出配置
    template_path: Optional[str] = None
    output_format: str = "both"  # "markdown", "json", "both"
    output_dir: Optional[Path] = None
    
    # 处理配置
    max_conversation_turns: int = 10
    enable_multimodal: bool = True
    enable_rag: bool = True
    
    def __post_init__(self) -> None:
        """初始化后处理。"""
        if self.output_dir and isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)


@dataclass
class PatentResult:
    """专利提取结果数据模型。
    
    用于封装提取结果和相关信息。
    """
    
    # 核心结果
    answer: str
    confidence_score: float
    
    # 格式化输出
    markdown_output: str
    json_output: str
    
    # 元数据
    processing_time: float
    tokens_used: int
    model_used: str
    
    # 相关文档片段
    relevant_sections: List[str]
    source_citations: List[str]
    
    # 多模态内容
    extracted_images: List[str]
    image_descriptions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        return {
            "answer": self.answer,
            "confidence_score": self.confidence_score,
            "markdown_output": self.markdown_output,
            "json_output": self.json_output,
            "processing_time": self.processing_time,
            "tokens_used": self.tokens_used,
            "model_used": self.model_used,
            "relevant_sections": self.relevant_sections,
            "source_citations": self.source_citations,
            "extracted_images": self.extracted_images,
            "image_descriptions": self.image_descriptions,
        }
