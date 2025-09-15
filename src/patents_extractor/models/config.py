"""模型配置管理模块。"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import logging


logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """模型配置类。
    
    定义了不同任务使用的模型配置。
    """
    
    # 文本处理模型
    text_model: str = "qwen-max"
    
    # OCR模型
    ocr_model: str = "qwen-vl-max"
    
    # 代码生成模型
    coder_model: str = "qwen-plus"
    
    # 视觉模型
    vision_model: str = "qwen-vl-max"
    
    # 多模态模型
    multimodal_model: str = "qwen-vl-max"
    
    # API配置
    api_base: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    api_key: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 4000
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        return {
            "text_model": self.text_model,
            "ocr_model": self.ocr_model,
            "coder_model": self.coder_model,
            "vision_model": self.vision_model,
            "multimodal_model": self.multimodal_model,
            "api_base": self.api_base,
            "api_key": self.api_key,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }


class ModelManager:
    """模型管理器。
    
    负责管理不同任务使用的模型配置。
    """
    
    def __init__(self, config: Optional[ModelConfig] = None):
        """初始化模型管理器。
        
        Args:
            config: 模型配置，如果为None则使用默认配置
        """
        self.config = config or ModelConfig()
        logger.info("模型管理器初始化完成")
        logger.info(f"文本模型: {self.config.text_model}")
        logger.info(f"OCR模型: {self.config.ocr_model}")
        logger.info(f"代码模型: {self.config.coder_model}")
        logger.info(f"视觉模型: {self.config.vision_model}")
        logger.info(f"多模态模型: {self.config.multimodal_model}")
    
    def get_text_model_config(self) -> Dict[str, Any]:
        """获取文本处理模型配置。
        
        Returns:
            文本模型配置字典
        """
        return {
            "model": self.config.text_model,
            "api_base": self.config.api_base,
            "api_key": self.config.api_key,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
    
    def get_ocr_model_config(self) -> Dict[str, Any]:
        """获取OCR模型配置。
        
        Returns:
            OCR模型配置字典
        """
        return {
            "model": self.config.ocr_model,
            "api_base": self.config.api_base,
            "api_key": self.config.api_key,
            "temperature": 0.0,  # OCR需要确定性输出
            "max_tokens": 2000,
        }
    
    def get_coder_model_config(self) -> Dict[str, Any]:
        """获取代码生成模型配置。
        
        Returns:
            代码模型配置字典
        """
        return {
            "model": self.config.coder_model,
            "api_base": self.config.api_base,
            "api_key": self.config.api_key,
            "temperature": 0.2,  # 代码生成需要一定的创造性
            "max_tokens": 6000,
        }
    
    def get_vision_model_config(self) -> Dict[str, Any]:
        """获取视觉模型配置。
        
        Returns:
            视觉模型配置字典
        """
        return {
            "model": self.config.vision_model,
            "api_base": self.config.api_base,
            "api_key": self.config.api_key,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
    
    def get_multimodal_model_config(self) -> Dict[str, Any]:
        """获取多模态模型配置。
        
        Returns:
            多模态模型配置字典
        """
        return {
            "model": self.config.multimodal_model,
            "api_base": self.config.api_base,
            "api_key": self.config.api_key,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
    
    def update_config(self, **kwargs) -> None:
        """更新模型配置。
        
        Args:
            **kwargs: 要更新的配置参数
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"更新配置: {key} = {value}")
            else:
                logger.warning(f"未知的配置参数: {key}")
    
    def get_model_info(self) -> Dict[str, str]:
        """获取所有模型信息。
        
        Returns:
            模型信息字典
        """
        return {
            "文本处理": self.config.text_model,
            "OCR识别": self.config.ocr_model,
            "代码生成": self.config.coder_model,
            "视觉理解": self.config.vision_model,
            "多模态": self.config.multimodal_model,
        }
