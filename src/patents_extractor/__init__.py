"""专利信息提取器 - 核心包初始化模块。

本包提供了基于LangGraph多Agent系统的专利信息智能提取功能。
"""

__version__ = "0.1.0"
__author__ = "jieke wu"
__email__ = "jieke.jack.wu@gmail.com"

# 导出主要API
from .core.extractor import PatentExtractor
from .core.workflow import PatentExtractionWorkflow
from .models.patent import PatentDocument, PatentQuery, PatentResult
from .models.state import PatentExtractionState
from .models.config import ModelConfig, ModelManager
from .agents.structured_node import StructuredAgentNode
from .agents.qa_node import QAAgentNode
from .agents.output_node import OutputAgentNode
from .agents.ocr_node import OCRAgentNode
from .agents.patent_localization_agent import PatentLocalizationAgent

__all__ = [
    "PatentExtractor",
    "PatentExtractionWorkflow",
    "PatentDocument",
    "PatentQuery", 
    "PatentResult",
    "PatentExtractionState",
    "ModelConfig",
    "ModelManager",
    "StructuredAgentNode",
    "QAAgentNode",
    "OutputAgentNode",
    "OCRAgentNode",
    "PatentLocalizationAgent",
]
