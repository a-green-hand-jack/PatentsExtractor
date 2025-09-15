"""测试Qwen模型调用。"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from patents_extractor import ModelConfig, ModelManager, PatentExtractor, PatentQuery


def test_model_config():
    """测试模型配置。"""
    print("=== 测试模型配置 ===")
    
    # 创建模型配置
    config = ModelConfig(
        api_key="sk-8281934e464f4e90a04dacc1ac444b4f",
        api_base="https://api.openai.com/v1",
        text_model="qwen3-max-preview-latest",
        ocr_model="qwen-vl-ocr-latest",
        coder_model="qwen3-coder-plus-latest",
        vision_model="qwen-vl-max-latest",
        multimodal_model="qvq-max-latest"
    )
    
    # 创建模型管理器
    manager = ModelManager(config)
    
    # 显示模型信息
    print("模型配置信息:")
    model_info = manager.get_model_info()
    for task, model in model_info.items():
        print(f"  {task}: {model}")
    
    # 测试各种模型配置
    print("\n各模型配置:")
    print("文本模型配置:", manager.get_text_model_config())
    print("OCR模型配置:", manager.get_ocr_model_config())
    print("代码模型配置:", manager.get_coder_model_config())
    print("视觉模型配置:", manager.get_vision_model_config())
    print("多模态模型配置:", manager.get_multimodal_model_config())


def test_simple_text_model():
    """测试简单的文本模型调用。"""
    print("\n=== 测试文本模型调用 ===")
    
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage
        
        # 创建模型配置
        config = ModelConfig(
            api_key="sk-8281934e464f4e90a04dacc1ac444b4f",
            api_base="https://api.openai.com/v1",
            text_model="qwen3-max-preview-latest"
        )
        
        # 创建ChatOpenAI实例
        model = ChatOpenAI(
            model=config.text_model,
            openai_api_base=config.api_base,
            openai_api_key=config.api_key,
            temperature=0.1,
            max_tokens=1000
        )
        
        # 测试简单调用
        response = model.invoke([HumanMessage(content="你好，请简单介绍一下你自己。")])
        print(f"模型响应: {response.content}")
        print("✅ 文本模型调用成功！")
        
    except Exception as e:
        print(f"❌ 文本模型调用失败: {e}")


def test_patent_extractor():
    """测试专利提取器。"""
    print("\n=== 测试专利提取器 ===")
    
    try:
        # 创建模型配置
        config = ModelConfig(
            api_key="sk-8281934e464f4e90a04dacc1ac444b4f",
            api_base="https://api.openai.com/v1",
            text_model="qwen3-max-preview-latest"
        )
        
        # 创建专利提取器
        extractor = PatentExtractor(config)
        
        # 创建测试查询（使用一个简单的文本作为输入源）
        query = PatentQuery(
            input_source="这是一个测试专利文档，包含关于蛋白质序列的技术内容。",
            question="这个专利的主要内容是什么？",
            output_format="both"
        )
        
        print("开始测试专利提取...")
        result = extractor.extract(query)
        
        print(f"✅ 专利提取成功！")
        print(f"答案: {result.answer}")
        print(f"置信度: {result.confidence_score}")
        print(f"处理时间: {result.processing_time:.2f}秒")
        print(f"使用模型: {result.model_used}")
        
    except Exception as e:
        print(f"❌ 专利提取器测试失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主测试函数。"""
    print("开始测试Qwen模型集成...")
    
    # 测试模型配置
    test_model_config()
    
    # 测试简单文本模型调用
    test_simple_text_model()
    
    # 测试专利提取器
    test_patent_extractor()
    
    print("\n测试完成！")


if __name__ == "__main__":
    main()
