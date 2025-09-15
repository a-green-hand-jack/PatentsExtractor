"""专利信息提取器核心模块。"""

import logging
from typing import Optional
from pathlib import Path

from .models.patent import PatentDocument, PatentQuery, PatentResult
from .agents.structured_agent import StructuredAgent
from .agents.qa_agent import QAAgent
from .agents.output_agent import OutputAgent


logger = logging.getLogger(__name__)


class PatentExtractor:
    """专利信息提取器主类。
    
    协调多个Agent完成专利信息的提取、问答和格式化输出。
    """
    
    def __init__(self) -> None:
        """初始化提取器。"""
        self.structured_agent = StructuredAgent()
        self.qa_agent = QAAgent()
        self.output_agent = OutputAgent()
        
        logger.info("专利提取器初始化完成")
    
    def extract(self, query: PatentQuery) -> PatentResult:
        """执行专利信息提取。
        
        Args:
            query: 专利查询请求
            
        Returns:
            提取结果
        """
        logger.info(f"开始处理专利查询: {query.question}")
        
        try:
            # 第一步：结构化处理
            logger.info("执行结构化处理...")
            patent_doc = self.structured_agent.process(query.input_source)
            
            # 第二步：问答处理
            logger.info("执行问答处理...")
            answer_result = self.qa_agent.answer(patent_doc, query.question)
            
            # 第三步：格式化输出
            logger.info("执行格式化输出...")
            result = self.output_agent.format_output(
                answer_result, 
                query.output_format,
                query.template_path
            )
            
            logger.info("专利信息提取完成")
            return result
            
        except Exception as e:
            logger.error(f"专利信息提取失败: {e}")
            raise
    
    def extract_with_conversation(self, query: PatentQuery) -> PatentResult:
        """支持多轮对话的专利信息提取。
        
        Args:
            query: 专利查询请求
            
        Returns:
            提取结果
        """
        logger.info("开始多轮对话式专利信息提取")
        
        # TODO: 实现多轮对话逻辑
        # 1. 引导用户完善问题描述
        # 2. 根据用户反馈调整查询策略
        # 3. 生成最终结果
        
        return self.extract(query)
