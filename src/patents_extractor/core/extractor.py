"""专利信息提取器核心模块。"""

import logging
from typing import Optional, Dict, Any

from .workflow import PatentExtractionWorkflow
from ..models.patent import PatentQuery, PatentResult
from ..models.config import ModelConfig


logger = logging.getLogger(__name__)


class PatentExtractor:
    """专利信息提取器主类。
    
    使用LangGraph工作流协调多个Agent完成专利信息的提取、问答和格式化输出。
    """
    
    def __init__(self, model_config: ModelConfig = None) -> None:
        """初始化提取器。
        
        Args:
            model_config: 模型配置，如果为None则使用默认配置
        """
        self.workflow = PatentExtractionWorkflow(model_config)
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
            # 使用工作流执行提取
            result = self.workflow.extract(
                input_source=query.input_source,
                question=query.question,
                output_format=query.output_format,
                template_path=query.template_path
            )
            
            # 转换为PatentResult对象
            patent_result = PatentResult(
                answer=result["answer"],
                confidence_score=result["confidence_score"],
                markdown_output=result["markdown_output"],
                json_output=result["json_output"],
                processing_time=result["processing_time"],
                tokens_used=result["tokens_used"],
                model_used=result["model_used"],
                relevant_sections=result["relevant_sections"],
                source_citations=result["source_citations"],
                extracted_images=result["extracted_images"],
                image_descriptions=result["image_descriptions"]
            )
            
            logger.info("专利信息提取完成")
            return patent_result
            
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
    
    def get_workflow_status(self, thread_id: str = "patent_extraction_session") -> Dict[str, Any]:
        """获取工作流状态。
        
        Args:
            thread_id: 线程ID
            
        Returns:
            工作流状态信息
        """
        return self.workflow.get_workflow_status(thread_id)
