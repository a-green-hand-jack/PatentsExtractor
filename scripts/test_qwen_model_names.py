"""测试Qwen模型名称。"""

import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


def test_qwen_models():
    """测试不同的Qwen模型名称。"""
    
    api_key = "sk-8281934e464f4e90a04dacc1ac444b4f"
    api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # 常见的Qwen模型名称
    model_names = [
        "qwen-max",
        "qwen-plus", 
        "qwen-turbo",
        "qwen2.5-max",
        "qwen2.5-plus",
        "qwen2.5-turbo",
        "qwen-vl-max",
        "qwen-vl-plus",
        "qwen-vl-turbo"
    ]
    
    for model_name in model_names:
        try:
            print(f"测试模型: {model_name}")
            
            model = ChatOpenAI(
                model=model_name,
                openai_api_base=api_base,
                openai_api_key=api_key,
                temperature=0.1,
                max_tokens=100
            )
            
            response = model.invoke([HumanMessage(content="你好")])
            print(f"✅ {model_name} 可用: {response.content[:50]}...")
            
        except Exception as e:
            print(f"❌ {model_name} 不可用: {e}")


if __name__ == "__main__":
    test_qwen_models()
