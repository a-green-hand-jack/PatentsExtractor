"""基于LangGraph的专利提取工作流。"""

import logging
import time
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from ..models.state import PatentExtractionState
from ..models.config import ModelManager, ModelConfig
from .structured_node import StructuredAgentNode
from .qa_node import QAAgentNode
from .output_node import OutputAgentNode


logger = logging.getLogger(__name__)


class PatentExtractionWorkflow:
    """专利提取工作流。
    
    使用LangGraph构建的多Agent工作流，协调各个Agent节点完成专利信息提取任务。
    """
    
    def __init__(self, model_config: ModelConfig = None):
        """初始化工作流。
        
        Args:
            model_config: 模型配置，如果为None则使用默认配置
        """
        # 初始化模型管理器
        self.model_manager = ModelManager(model_config)
        
        # 初始化各个Agent节点
        self.structured_node = StructuredAgentNode(self.model_manager)
        self.qa_node = QAAgentNode(self.model_manager)
        self.output_node = OutputAgentNode()
        
        # 构建工作流图
        self.graph = self._build_graph()
        
        logger.info("专利提取工作流初始化完成")
        logger.info(f"使用的模型: {self.model_manager.get_model_info()}")
    
    def _build_graph(self) -> StateGraph:
        """构建工作流图。
        
        Returns:
            构建的StateGraph对象
        """
        # 创建状态图
        workflow = StateGraph(PatentExtractionState)
        
        # 添加节点
        workflow.add_node("structured_processing", self.structured_node.process)
        workflow.add_node("qa_processing", self.qa_node.process)
        workflow.add_node("output_formatting", self.output_node.process)
        
        # 定义工作流路径
        workflow.set_entry_point("structured_processing")
        
        workflow.add_edge("structured_processing", "qa_processing")
        workflow.add_edge("qa_processing", "output_formatting")
        workflow.add_edge("output_formatting", END)
        
        # 添加错误处理
        workflow.add_edge("structured_processing", END, condition=self._has_error)
        workflow.add_edge("qa_processing", END, condition=self._has_error)
        workflow.add_edge("output_formatting", END, condition=self._has_error)
        
        # 编译图
        return workflow.compile(checkpointer=MemorySaver())
    
    def _has_error(self, state: PatentExtractionState) -> bool:
        """检查状态中是否有错误。
        
        Args:
            state: 当前状态
            
        Returns:
            是否有错误
        """
        return state.get("error_message") is not None
    
    def extract(self, input_source: str, question: str, output_format: str = "both", template_path: str = None) -> Dict[str, Any]:
        """执行专利信息提取。
        
        Args:
            input_source: 输入源（PDF文件路径或网页URL）
            question: 用户问题
            output_format: 输出格式
            template_path: 自定义模板路径
            
        Returns:
            提取结果
        """
        logger.info(f"开始专利信息提取: {input_source}")
        start_time = time.time()
        
        try:
            # 初始化状态
            initial_state = PatentExtractionState(
                input_source=input_source,
                question=question,
                template_path=template_path,
                output_format=output_format,
                raw_content=None,
                structured_content=None,
                patent_document=None,
                answer=None,
                confidence_score=None,
                relevant_sections=None,
                source_citations=None,
                markdown_output=None,
                json_output=None,
                processing_time=None,
                tokens_used=None,
                model_used=None,
                error_message=None,
                extracted_images=None,
                image_descriptions=None,
                current_step="initialization",
                completed_steps=[],
                next_step=None
            )
            
            # 执行工作流
            config = {"configurable": {"thread_id": "patent_extraction_session"}}
            final_state = self.graph.invoke(initial_state, config=config)
            
            # 计算处理时间
            processing_time = time.time() - start_time
            final_state["processing_time"] = processing_time
            
            # 构建结果
            result = {
                "answer": final_state.get("answer", ""),
                "confidence_score": final_state.get("confidence_score", 0.0),
                "markdown_output": final_state.get("markdown_output", ""),
                "json_output": final_state.get("json_output", ""),
                "processing_time": processing_time,
                "tokens_used": final_state.get("tokens_used", 0),
                "model_used": final_state.get("model_used", self.model_name),
                "relevant_sections": final_state.get("relevant_sections", []),
                "source_citations": final_state.get("source_citations", []),
                "extracted_images": final_state.get("extracted_images", []),
                "image_descriptions": final_state.get("image_descriptions", []),
                "error_message": final_state.get("error_message"),
                "completed_steps": final_state.get("completed_steps", [])
            }
            
            logger.info(f"专利信息提取完成，耗时: {processing_time:.2f}秒")
            return result
            
        except Exception as e:
            logger.error(f"专利信息提取失败: {e}")
            return {
                "answer": "",
                "confidence_score": 0.0,
                "markdown_output": "",
                "json_output": "",
                "processing_time": time.time() - start_time,
                "tokens_used": 0,
                "model_used": self.model_name,
                "relevant_sections": [],
                "source_citations": [],
                "extracted_images": [],
                "image_descriptions": [],
                "error_message": str(e),
                "completed_steps": []
            }
    
    def get_workflow_status(self, thread_id: str = "patent_extraction_session") -> Dict[str, Any]:
        """获取工作流状态。
        
        Args:
            thread_id: 线程ID
            
        Returns:
            工作流状态信息
        """
        try:
            config = {"configurable": {"thread_id": thread_id}}
            state = self.graph.get_state(config)
            
            return {
                "current_step": state.values.get("current_step", "unknown"),
                "completed_steps": state.values.get("completed_steps", []),
                "next_step": state.values.get("next_step"),
                "error_message": state.values.get("error_message"),
                "is_complete": state.next == (),
                "is_error": state.values.get("error_message") is not None
            }
        except Exception as e:
            logger.error(f"获取工作流状态失败: {e}")
            return {
                "current_step": "error",
                "completed_steps": [],
                "next_step": None,
                "error_message": str(e),
                "is_complete": False,
                "is_error": True
            }
