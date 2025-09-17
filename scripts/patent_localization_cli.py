#!/usr/bin/env python3
"""专利本地化命令行工具。

提供简单的命令行接口来使用专利本地化功能。
"""

import sys
from pathlib import Path

# 将项目根目录下的 src 目录添加到 Python 解释器的搜索路径中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import argparse
import logging
from patents_extractor import PatentLocalizationAgent

def setup_logging(verbose: bool = False):
    """设置日志配置。"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """主函数：命令行接口。"""
    parser = argparse.ArgumentParser(
        description="专利网页本地化工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python scripts/patent_localization_cli.py "https://patents.google.com/patent/CN116555216A/en"
  python scripts/patent_localization_cli.py "https://patents.google.com/patent/CN116555216A/en" -o ./output
  python scripts/patent_localization_cli.py "https://patents.google.com/patent/CN116555216A/en" -v
        """
    )
    
    parser.add_argument(
        "url",
        help="专利网页URL"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("output/patents"),
        help="输出目录 (默认: output/patents)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="详细输出"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="请求超时时间（秒） (默认: 30)"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=2,
        help="最大重试次数 (默认: 2)"
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.verbose)
    
    print(f"专利网页本地化工具")
    print(f"URL: {args.url}")
    print(f"输出目录: {args.output}")
    print(f"超时时间: {args.timeout}秒")
    print(f"最大重试次数: {args.max_retries}")
    print("-" * 50)
    
    try:
        # 创建Agent
        agent = PatentLocalizationAgent(
            timeout=args.timeout,
            max_retries=args.max_retries
        )
        
        # 执行本地化
        result = agent.localize_patent(args.url, args.output)
        
        # 输出结果
        print("\n本地化结果:")
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
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生异常: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

