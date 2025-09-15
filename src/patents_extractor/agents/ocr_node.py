"""基于LangGraph的OCR Agent节点。"""

import logging
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..models.state import PatentExtractionState
from ..models.config import ModelManager


logger = logging.getLogger(__name__)


class OCRAgentNode:
    """OCR Agent节点。
    
    负责使用Qwen-VL-OCR模型处理图片中的文字识别。
    """
    
    def __init__(self, model_manager: ModelManager):
        """初始化OCR Agent节点。
        
        Args:
            model_manager: 模型管理器
        """
        self.model_manager = model_manager
        
        # 使用OCR模型
        ocr_config = model_manager.get_ocr_model_config()
        self.model = ChatOpenAI(
            model=ocr_config["model"],
            openai_api_base=ocr_config["api_base"],
            openai_api_key=ocr_config["api_key"],
            temperature=ocr_config["temperature"],
            max_tokens=ocr_config["max_tokens"]
        )
        
        logger.info(f"OCR Agent节点初始化完成，使用模型: {ocr_config['model']}")
    
    def process_images(self, images: List[str]) -> List[str]:
        """处理图片列表，提取文字内容。
        
        Args:
            images: 图片路径或URL列表
            
        Returns:
            提取的文字内容列表
        """
        logger.info(f"开始OCR处理，图片数量: {len(images)}")
        
        extracted_texts = []
        
        for i, image_path in enumerate(images):
            try:
                logger.info(f"处理第{i+1}张图片: {image_path}")
                
                # 构建OCR提示词
                prompt = self._build_ocr_prompt(image_path)
                
                # 调用OCR模型
                messages = [
                    SystemMessage(content="你是一个专业的OCR识别助手，能够准确识别图片中的文字内容。请只返回识别出的文字，不要添加任何解释。"),
                    HumanMessage(content=prompt)
                ]
                
                response = self.model.invoke(messages)
                extracted_text = response.content.strip()
                
                extracted_texts.append(extracted_text)
                logger.info(f"第{i+1}张图片OCR完成，识别文字长度: {len(extracted_text)}")
                
            except Exception as e:
                logger.error(f"第{i+1}张图片OCR失败: {e}")
                extracted_texts.append(f"OCR失败: {str(e)}")
        
        logger.info(f"OCR处理完成，成功处理: {len([t for t in extracted_texts if not t.startswith('OCR失败')])}张图片")
        return extracted_texts
    
    def _build_ocr_prompt(self, image_path: str) -> str:
        """构建OCR提示词。
        
        Args:
            image_path: 图片路径或URL
            
        Returns:
            构建的提示词
        """
        # 根据图片路径类型构建不同的提示词
        if image_path.startswith(("http://", "https://")):
            prompt = f"请识别以下图片中的文字内容：\n![图片]({image_path})"
        else:
            prompt = f"请识别以下本地图片中的文字内容：\n![图片]({image_path})"
        
        return prompt
    
    def extract_text_from_pdf_images(self, pdf_images: List[Dict[str, Any]]) -> List[str]:
        """从PDF图片中提取文字。
        
        Args:
            pdf_images: PDF图片信息列表，每个包含data、width、height等字段
            
        Returns:
            提取的文字内容列表
        """
        logger.info(f"开始从PDF图片中提取文字，图片数量: {len(pdf_images)}")
        
        extracted_texts = []
        
        for i, img_info in enumerate(pdf_images):
            try:
                logger.info(f"处理第{i+1}张PDF图片，尺寸: {img_info['width']}x{img_info['height']}")
                
                # 对于PDF中的图片，我们需要将图片数据转换为base64或保存为临时文件
                # 这里简化处理，假设图片数据可以直接使用
                img_data = img_info.get("data", "")
                
                if img_data:
                    # 构建OCR提示词
                    prompt = f"请识别以下图片中的文字内容：\n![图片数据](data:image/png;base64,{img_data})"
                    
                    # 调用OCR模型
                    messages = [
                        SystemMessage(content="你是一个专业的OCR识别助手，能够准确识别图片中的文字内容。请只返回识别出的文字，不要添加任何解释。"),
                        HumanMessage(content=prompt)
                    ]
                    
                    response = self.model.invoke(messages)
                    extracted_text = response.content.strip()
                    
                    extracted_texts.append(extracted_text)
                    logger.info(f"第{i+1}张PDF图片OCR完成，识别文字长度: {len(extracted_text)}")
                else:
                    logger.warning(f"第{i+1}张PDF图片没有数据")
                    extracted_texts.append("")
                
            except Exception as e:
                logger.error(f"第{i+1}张PDF图片OCR失败: {e}")
                extracted_texts.append(f"OCR失败: {str(e)}")
        
        logger.info(f"PDF图片OCR处理完成")
        return extracted_texts
