"""数据模型定义模块。"""

from .patent import PatentDocument, PatentQuery, PatentResult
from .state import PatentExtractionState

__all__ = ["PatentDocument", "PatentQuery", "PatentResult", "PatentExtractionState"]
