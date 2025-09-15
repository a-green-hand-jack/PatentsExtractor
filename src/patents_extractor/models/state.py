"""LangGraph状态模型定义。"""

from typing import TypedDict, List, Optional, Dict, Any
from datetime import datetime


class PatentExtractionState(TypedDict):
    """专利提取工作流状态。
    
    定义了整个专利提取过程中需要传递的状态信息。
    """
    
    # 输入信息
    input_source: str  # PDF文件路径或网页URL
    question: str  # 用户问题
    template_path: Optional[str]  # 自定义模板路径
    output_format: str  # 输出格式
    
    # 中间处理结果
    raw_content: Optional[str]  # 原始内容
    structured_content: Optional[Dict[str, Any]]  # 结构化内容
    patent_document: Optional[Dict[str, Any]]  # 专利文档对象
    
    # 问答结果
    answer: Optional[str]  # 生成的答案
    confidence_score: Optional[float]  # 置信度
    relevant_sections: Optional[List[str]]  # 相关文档片段
    source_citations: Optional[List[str]]  # 引用来源
    
    # 输出结果
    markdown_output: Optional[str]  # Markdown格式输出
    json_output: Optional[str]  # JSON格式输出
    
    # 元数据
    processing_time: Optional[float]  # 处理时间
    tokens_used: Optional[int]  # 使用的Token数量
    model_used: Optional[str]  # 使用的模型
    error_message: Optional[str]  # 错误信息
    
    # 多模态内容
    extracted_images: Optional[List[str]]  # 提取的图片
    image_descriptions: Optional[List[str]]  # 图片描述
    
    # 工作流控制
    current_step: str  # 当前步骤
    completed_steps: List[str]  # 已完成的步骤
    next_step: Optional[str]  # 下一步骤
