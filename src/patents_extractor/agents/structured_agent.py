"""结构化Agent实现。

负责将非结构化的PDF或网页内容转换为结构化数据。
"""

import logging
from pathlib import Path
from typing import Union
from datetime import datetime

from ..models.patent import PatentDocument
from ..utils.file_utils import FileProcessor
from ..utils.web_utils import WebProcessor
from ..utils.pdf_utils import PDFProcessor


logger = logging.getLogger(__name__)


class StructuredAgent:
    """结构化Agent。
    
    负责将PDF文件或网页内容转换为结构化的专利文档。
    """
    
    def __init__(self) -> None:
        """初始化结构化Agent。"""
        self.file_processor = FileProcessor()
        self.web_processor = WebProcessor()
        self.pdf_processor = PDFProcessor()
        
        logger.info("结构化Agent初始化完成")
    
    def process(self, input_source: str) -> PatentDocument:
        """处理输入源并返回结构化专利文档。
        
        Args:
            input_source: 输入源（PDF文件路径或网页URL）
            
        Returns:
            结构化的专利文档
        """
        logger.info(f"开始处理输入源: {input_source}")
        
        # 判断输入类型
        if self._is_url(input_source):
            return self._process_web(input_source)
        elif self._is_pdf_file(input_source):
            return self._process_pdf(input_source)
        else:
            raise ValueError(f"不支持的输入类型: {input_source}")
    
    def _is_url(self, source: str) -> bool:
        """判断是否为URL。"""
        return source.startswith(("http://", "https://"))
    
    def _is_pdf_file(self, source: str) -> bool:
        """判断是否为PDF文件。"""
        path = Path(source)
        return path.exists() and path.suffix.lower() == ".pdf"
    
    def _process_web(self, url: str) -> PatentDocument:
        """处理网页内容。
        
        Args:
            url: 网页URL
            
        Returns:
            结构化的专利文档
        """
        logger.info(f"处理网页内容: {url}")
        
        # 使用WebProcessor提取网页内容
        web_content = self.web_processor.extract_content(url)
        
        # 转换为专利文档格式
        patent_doc = PatentDocument(
            title=web_content.get("title", ""),
            abstract=web_content.get("abstract", ""),
            inventors=web_content.get("inventors", []),
            assignee=web_content.get("assignee", ""),
            publication_number=web_content.get("publication_number", ""),
            publication_date=datetime.now(),  # TODO: 解析实际日期
            description=web_content.get("description", ""),
            claims=web_content.get("claims", ""),
            drawings=web_content.get("drawings", []),
            source_type="web",
            source_path=url,
            extraction_time=datetime.now(),
            structured_content=web_content
        )
        
        logger.info("网页内容处理完成")
        return patent_doc
    
    def _process_pdf(self, pdf_path: str) -> PatentDocument:
        """处理PDF文件。
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            结构化的专利文档
        """
        logger.info(f"处理PDF文件: {pdf_path}")
        
        # 使用PDFProcessor提取PDF内容
        pdf_content = self.pdf_processor.extract_content(pdf_path)
        
        # 转换为专利文档格式
        patent_doc = PatentDocument(
            title=pdf_content.get("title", ""),
            abstract=pdf_content.get("abstract", ""),
            inventors=pdf_content.get("inventors", []),
            assignee=pdf_content.get("assignee", ""),
            publication_number=pdf_content.get("publication_number", ""),
            publication_date=datetime.now(),  # TODO: 解析实际日期
            description=pdf_content.get("description", ""),
            claims=pdf_content.get("claims", ""),
            drawings=pdf_content.get("drawings", []),
            source_type="pdf",
            source_path=pdf_path,
            extraction_time=datetime.now(),
            structured_content=pdf_content
        )
        
        logger.info("PDF文件处理完成")
        return patent_doc
