"""基于LangGraph的结构化Agent节点。"""

import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage

from ..models.state import PatentExtractionState
from ..models.config import ModelManager
from ..utils.web_utils import WebProcessor
from ..utils.pdf_utils import PDFProcessor
from .ocr_node import OCRAgentNode


logger = logging.getLogger(__name__)


class StructuredAgentNode:
    """结构化Agent节点。
    
    负责将PDF或网页内容转换为结构化数据。
    """
    
    def __init__(self, model_manager: ModelManager = None):
        """初始化结构化Agent节点。
        
        Args:
            model_manager: 模型管理器，如果为None则创建默认管理器
        """
        self.model_manager = model_manager or ModelManager()
        self.web_processor = WebProcessor()
        self.pdf_processor = PDFProcessor()
        self.ocr_agent = OCRAgentNode(self.model_manager)
        
        logger.info("结构化Agent节点初始化完成")
    
    def process(self, state: PatentExtractionState) -> PatentExtractionState:
        """处理输入源并返回结构化内容。
        
        Args:
            state: 当前工作流状态
            
        Returns:
            更新后的状态
        """
        logger.info(f"开始结构化处理: {state['input_source']}")
        
        try:
            # 更新当前步骤
            state["current_step"] = "structured_processing"
            state["completed_steps"].append("structured_processing")
            
            # 判断输入类型并处理
            if self._is_url(state["input_source"]):
                structured_content = self._process_web(state["input_source"])
            elif self._is_pdf_file(state["input_source"]):
                structured_content = self._process_pdf(state["input_source"])
            else:
                raise ValueError(f"不支持的输入类型: {state['input_source']}")
            
            # 处理图片OCR
            if structured_content.get("drawings"):
                logger.info("开始处理图片OCR")
                ocr_results = self._process_images_ocr(structured_content["drawings"])
                structured_content["image_descriptions"] = ocr_results
            
            # 更新状态
            state["structured_content"] = structured_content
            state["raw_content"] = structured_content.get("raw_text", "")
            state["extracted_images"] = structured_content.get("drawings", [])
            state["image_descriptions"] = structured_content.get("image_descriptions", [])
            state["next_step"] = "qa_processing"
            
            logger.info("结构化处理完成")
            return state
            
        except Exception as e:
            logger.error(f"结构化处理失败: {e}")
            state["error_message"] = str(e)
            state["next_step"] = END
            return state
    
    def _is_url(self, source: str) -> bool:
        """判断是否为URL。"""
        return source.startswith(("http://", "https://"))
    
    def _is_pdf_file(self, source: str) -> bool:
        """判断是否为PDF文件。"""
        from pathlib import Path
        path = Path(source)
        return path.exists() and path.suffix.lower() == ".pdf"
    
    def _process_web(self, url: str) -> Dict[str, Any]:
        """处理网页内容。"""
        logger.info(f"处理网页内容: {url}")
        return self.web_processor.extract_content(url)
    
    def _process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """处理PDF文件。"""
        logger.info(f"处理PDF文件: {pdf_path}")
        return self.pdf_processor.extract_content(pdf_path)
    
    def _process_images_ocr(self, images: list) -> list[str]:
        """处理图片OCR。
        
        Args:
            images: 图片列表
            
        Returns:
            OCR识别结果列表
        """
        if not images:
            return []
        
        # 判断图片类型
        if isinstance(images[0], dict):
            # PDF图片数据
            return self.ocr_agent.extract_text_from_pdf_images(images)
        else:
            # 普通图片路径
            return self.ocr_agent.process_images(images)
