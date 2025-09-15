#!/usr/bin/env python3
"""专利本地化Agent功能演示脚本 - FastMCP版本。"""

import sys
import asyncio
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from patents_extractor.agents.patent_localization_agent import PatentLocalizationAgent
from patents_extractor.models.config import ModelManager


async def main():
    """主函数：演示专利本地化功能。"""
    print("=== 专利本地化Agent功能演示 - FastMCP版本 ===\n")
    
    # 初始化模型管理器
    print("1. 初始化模型管理器...")
    model_manager = ModelManager()
    print("✓ 模型管理器初始化完成\n")
    
    # 初始化专利本地化Agent
    print("2. 初始化专利本地化Agent...")
    agent = PatentLocalizationAgent(model_manager)
    print("✓ 专利本地化Agent初始化完成\n")
    
    # 设置测试URL和输出目录
    test_url = "https://patents.google.com/patent/CN116555216A/en?oq=CN+116555216+A"
    output_dir = Path("./output/patents")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"3. 开始本地化专利: {test_url}")
    print(f"   输出目录: {output_dir}")
    
    try:
        # 运行专利本地化
        result = await agent.localize_patent(test_url, output_dir)
        
        print(f"\n4. 本地化结果:")
        print(f"   状态: {result['status']}")
        print(f"   专利ID: {result['patent_id']}")
        print(f"   专利文件夹: {result['patent_folder']}")
        
        if result['status'] == 'success':
            print(f"   Markdown文件: {result['markdown_file']}")
            print(f"   图片文件夹: {result['images_folder']}")
            print(f"   下载的图片数量: {len(result.get('downloaded_images', []))}")
            print(f"   进度文件: {result['progress_file']}")
            
            # 显示文件内容预览
            markdown_file = Path(result['markdown_file'])
            if markdown_file.exists():
                content = markdown_file.read_text(encoding='utf-8')
                print(f"\n5. Markdown文件内容预览 (前500字符):")
                print("-" * 50)
                print(content[:500])
                if len(content) > 500:
                    print("...")
                print("-" * 50)
        else:
            print(f"   错误信息: {result.get('error', '未知错误')}")
        
        print(f"\n✓ 专利本地化完成!")
        
    except Exception as e:
        print(f"\n✗ 专利本地化失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    # 运行异步主函数
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
