"""专利提取器使用示例。"""

import os
from pathlib import Path

from patents_extractor import PatentExtractor, PatentQuery, ModelConfig


def main():
    """主函数示例。"""
    
    # 配置模型
    model_config = ModelConfig(
        api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),
        api_base="https://api.openai.com/v1",  # 或者你的Qwen API端点
        text_model="qwen3-max-preview-latest",
        ocr_model="qwen-vl-ocr-latest",
        coder_model="qwen3-coder-plus-latest",
        vision_model="qwen-vl-max-latest",
        multimodal_model="qvq-max-latest"
    )
    
    # 初始化提取器
    extractor = PatentExtractor(model_config)
    
    # 示例1: 从PDF文件提取信息
    print("=== 示例1: PDF文件提取 ===")
    pdf_query = PatentQuery(
        input_source="data/patents/TdT/CN118284690A.pdf",
        question="权利要求书中关于蛋白质的氨基酸序列的要求",
        output_format="both"
    )
    
    try:
        result = extractor.extract(pdf_query)
        print(f"答案: {result.answer}")
        print(f"置信度: {result.confidence_score}")
        print(f"处理时间: {result.processing_time:.2f}秒")
        print(f"使用模型: {result.model_used}")
        
        # 保存结果
        output_dir = Path("output/results")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if result.markdown_output:
            markdown_file = output_dir / "pdf_result.md"
            markdown_file.write_text(result.markdown_output, encoding="utf-8")
            print(f"Markdown结果已保存到: {markdown_file}")
        
        if result.json_output:
            json_file = output_dir / "pdf_result.json"
            json_file.write_text(result.json_output, encoding="utf-8")
            print(f"JSON结果已保存到: {json_file}")
            
    except Exception as e:
        print(f"PDF提取失败: {e}")
    
    # 示例2: 从网页链接提取信息
    print("\n=== 示例2: 网页链接提取 ===")
    web_query = PatentQuery(
        input_source="https://patents.google.com/patent/US12345678",
        question="发明的主要技术特征是什么？",
        output_format="markdown"
    )
    
    try:
        result = extractor.extract(web_query)
        print(f"答案: {result.answer}")
        print(f"相关文档片段: {result.relevant_sections}")
        
        # 保存结果
        if result.markdown_output:
            markdown_file = output_dir / "web_result.md"
            markdown_file.write_text(result.markdown_output, encoding="utf-8")
            print(f"Markdown结果已保存到: {markdown_file}")
            
    except Exception as e:
        print(f"网页提取失败: {e}")
    
    # 示例3: 查看工作流状态
    print("\n=== 示例3: 工作流状态 ===")
    status = extractor.get_workflow_status()
    print(f"当前步骤: {status['current_step']}")
    print(f"已完成步骤: {status['completed_steps']}")
    print(f"是否完成: {status['is_complete']}")
    print(f"是否有错误: {status['is_error']}")


if __name__ == "__main__":
    main()
