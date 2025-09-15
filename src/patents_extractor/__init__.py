"""专利信息提取器 - 核心包初始化模块。

本包提供了基于多Agent系统的专利信息智能提取功能。
"""

__version__ = "0.1.0"
__author__ = "a-green-hand-jack"
__email__ = "your-email@example.com"

# 导出主要API
from .core.extractor import PatentExtractor
from .models.patent import PatentDocument, PatentQuery, PatentResult
from .agents.structured_agent import StructuredAgent
from .agents.qa_agent import QAAgent
from .agents.output_agent import OutputAgent

__all__ = [
    "PatentExtractor",
    "PatentDocument",
    "PatentQuery", 
    "PatentResult",
    "StructuredAgent",
    "QAAgent",
    "OutputAgent",
]
