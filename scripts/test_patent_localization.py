#!/usr/bin/env python3
"""测试专利本地化Agent的脚本。"""

import sys
from pathlib import Path

# 将项目根目录下的 src 目录添加到 Python 解释器的搜索路径中
# 这使得脚本可以直接导入 src/patents_extractor 中的模块
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import logging
from patents_extractor import PatentLocalizationAgent, ModelManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def test_patent_localization():
    """测试专利本地化功能。"""
    
    # 测试URL
    test_url = "https://patents.google.com/patent/CN116555216A/en?oq=CN+116555216+A"
    
    # 输出目录
    output_dir = Path("output/patents")
    
    logger.info(f"开始测试专利本地化: {test_url}")
    
    try:
        # 创建模型管理器
        model_manager = ModelManager()
        
        # 创建专利本地化Agent
        localization_agent = PatentLocalizationAgent(model_manager)
        
        # 执行本地化
        result = localization_agent.localize_patent(test_url, output_dir)
        
        # 输出结果
        logger.info("专利本地化结果:")
        logger.info(f"专利ID: {result['patent_id']}")
        
        if result['status'] == 'success':
            logger.info(f"专利文件夹: {result['patent_folder']}")
            logger.info(f"创建的文件: {result['files_created']}")
            logger.info(f"下载的图片数量: {result['images_downloaded']}")
            logger.info(f"状态: {result['status']}")
            
            logger.info("✅ 专利本地化测试成功!")
            
            # 检查生成的文件
            patent_folder = Path(result['patent_folder'])
            for file_name in result['files_created']:
                file_path = patent_folder / file_name
                if file_path.exists():
                    logger.info(f"✅ 文件存在: {file_path}")
                    if file_name == "patent.md":
                        # 显示Markdown文件的前几行
                        content = file_path.read_text(encoding='utf-8')
                        logger.info("专利Markdown内容预览:")
                        logger.info(content[:500] + "..." if len(content) > 500 else content)
                else:
                    logger.warning(f"❌ 文件不存在: {file_path}")
            
            # 检查图片文件夹
            images_folder = patent_folder / "images"
            if images_folder.exists():
                image_files = list(images_folder.glob("*.png"))
                logger.info(f"✅ 图片文件夹存在，包含 {len(image_files)} 个图片文件")
                for img_file in image_files:
                    logger.info(f"  - {img_file.name}")
            else:
                logger.warning("❌ 图片文件夹不存在")
                
        else:
            logger.error(f"错误: {result.get('error', '未知错误')}")
            logger.error(f"状态: {result['status']}")
            return
            
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        raise


if __name__ == "__main__":
    test_patent_localization()
