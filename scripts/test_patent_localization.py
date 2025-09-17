#!/usr/bin/env python3
"""专利本地化Agent测试脚本。

测试专利网页本地化功能，使用Google Patents的专利页面作为测试用例。
"""

import sys
from pathlib import Path

# 将项目根目录下的 src 目录添加到 Python 解释器的搜索路径中
# 这使得脚本可以直接导入 src/patents_extractor 中的模块
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import logging
from patents_extractor import PatentLocalizationAgent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """主函数：测试专利本地化功能。"""
    
    # 测试URL
    test_url = "https://patents.google.com/patent/CN116555216A/en?oq=CN+116555216+A"
    
    # 输出目录
    output_dir = Path("output/patents")
    
    print(f"开始测试专利本地化功能")
    print(f"测试URL: {test_url}")
    print(f"输出目录: {output_dir}")
    print("-" * 50)
    
    try:
        # 创建Agent
        agent = PatentLocalizationAgent()
        
        # 执行本地化
        result = agent.localize_patent(test_url, output_dir)
        
        # 输出结果
        print("本地化结果:")
        print(f"  专利编号: {result.get('patent_id', 'N/A')}")
        print(f"  专利文件夹: {result.get('patent_folder', 'N/A')}")
        print(f"  创建的文件: {result.get('files_created', [])}")
        print(f"  下载的资源数: {result.get('resources_downloaded', 0)}")
        print(f"  状态: {result.get('status', 'N/A')}")
        
        if result.get('status') == 'success':
            print("\n✅ 专利本地化成功完成！")
            
            # 显示生成的文件
            patent_folder = Path(result['patent_folder'])
            if patent_folder.exists():
                print(f"\n生成的文件:")
                for file_path in patent_folder.rglob('*'):
                    if file_path.is_file():
                        print(f"  - {file_path.relative_to(patent_folder)}")
        else:
            print(f"\n❌ 专利本地化失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

