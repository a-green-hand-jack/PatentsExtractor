"""基于LangGraph的问答Agent节点。"""

import logging
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..models.state import PatentExtractionState
from ..models.config import ModelManager


logger = logging.getLogger(__name__)


class QAAgentNode:
    """问答Agent节点。
    
    负责基于结构化内容回答用户问题。
    """
    
    def __init__(self, model_manager: ModelManager):
        """初始化问答Agent节点。
        
        Args:
            model_manager: 模型管理器
        """
        self.model_manager = model_manager
        
        # 使用文本处理模型
        text_config = model_manager.get_text_model_config()
        self.model = ChatOpenAI(
            model=text_config["model"],
            openai_api_base=text_config["api_base"],
            openai_api_key=text_config["api_key"],
            temperature=text_config["temperature"],
            max_tokens=text_config["max_tokens"]
        )
        
        logger.info(f"问答Agent节点初始化完成，使用模型: {text_config['model']}")
    
    def process(self, state: PatentExtractionState) -> PatentExtractionState:
        """处理问答任务。
        
        Args:
            state: 当前工作流状态
            
        Returns:
            更新后的状态
        """
        logger.info(f"开始问答处理: {state['question']}")
        
        try:
            # 更新当前步骤
            state["current_step"] = "qa_processing"
            state["completed_steps"].append("qa_processing")
            
            # 构建提示词
            prompt = self._build_prompt(state)
            
            # 调用语言模型
            messages = [
                SystemMessage(content="你是一个专业的专利信息提取助手，能够准确回答关于专利内容的问题。"),
                HumanMessage(content=prompt)
            ]
            
            response = self.model.invoke(messages)
            answer = response.content
            
            # 解析答案和置信度
            confidence_score = self._calculate_confidence(answer, state)
            
            # 提取相关文档片段
            relevant_sections = self._extract_relevant_sections(state)
            
            # 更新状态
            state["answer"] = answer
            state["confidence_score"] = confidence_score
            state["relevant_sections"] = relevant_sections
            state["source_citations"] = [state["structured_content"].get("publication_number", "")]
            state["model_used"] = self.model_manager.config.text_model
            state["next_step"] = "output_formatting"
            
            logger.info("问答处理完成")
            return state
            
        except Exception as e:
            logger.error(f"问答处理失败: {e}")
            state["error_message"] = str(e)
            state["next_step"] = END
            return state
    
    def _build_prompt(self, state: PatentExtractionState) -> str:
        """构建提示词。
        
        Args:
            state: 当前状态
            
        Returns:
            构建的提示词
        """
        structured_content = state["structured_content"]
        question = state["question"]
        
        prompt = f"""
请基于以下专利信息回答用户的问题：

专利标题: {structured_content.get('title', '')}
专利摘要: {structured_content.get('abstract', '')}
发明人: {', '.join(structured_content.get('inventors', []))}
专利权人: {structured_content.get('assignee', '')}
公开号: {structured_content.get('publication_number', '')}

专利描述: {structured_content.get('description', '')[:2000]}...

权利要求: {structured_content.get('claims', '')[:2000]}...

用户问题: {question}

请提供准确、详细的回答，并说明你的回答基于专利文档的哪些部分。
"""
        return prompt
    
    def _calculate_confidence(self, answer: str, state: PatentExtractionState) -> float:
        """计算答案的置信度。
        
        Args:
            answer: 生成的答案
            state: 当前状态
            
        Returns:
            置信度分数 (0-1)
        """
        # 简单的置信度计算逻辑
        # TODO: 实现更复杂的置信度计算
        
        if not answer or len(answer) < 10:
            return 0.1
        
        # 基于答案长度和内容质量
        confidence = min(0.9, 0.3 + len(answer) / 1000)
        
        # 检查是否包含具体信息
        if any(keyword in answer.lower() for keyword in ['序列', '氨基酸', '蛋白质', '权利要求']):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _extract_relevant_sections(self, state: PatentExtractionState) -> list[str]:
        """提取相关文档片段。
        
        Args:
            state: 当前状态
            
        Returns:
            相关文档片段列表
        """
        structured_content = state["structured_content"]
        question = state["question"].lower()
        
        relevant_sections = []
        
        # 根据问题类型选择相关片段
        if any(keyword in question for keyword in ['权利要求', 'claim']):
            claims = structured_content.get('claims', '')
            if claims:
                relevant_sections.append(f"权利要求: {claims[:500]}...")
        
        if any(keyword in question for keyword in ['摘要', 'abstract']):
            abstract = structured_content.get('abstract', '')
            if abstract:
                relevant_sections.append(f"摘要: {abstract}")
        
        if any(keyword in question for keyword in ['描述', 'description']):
            description = structured_content.get('description', '')
            if description:
                relevant_sections.append(f"描述: {description[:500]}...")
        
        # 如果没有特定匹配，返回基本信息
        if not relevant_sections:
            title = structured_content.get('title', '')
            if title:
                relevant_sections.append(f"专利标题: {title}")
        
        return relevant_sections
