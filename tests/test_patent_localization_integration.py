"""专利本地化Agent集成测试 - FastMCP版本。"""

import unittest
import asyncio
from pathlib import Path
import tempfile
import shutil

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from patents_extractor.agents.patent_localization_agent import PatentLocalizationAgent
from patents_extractor.models.config import ModelManager


class TestPatentLocalizationIntegration(unittest.TestCase):
    """专利本地化Agent集成测试类 - FastMCP版本。"""
    
    def setUp(self):
        """设置测试环境。"""
        self.model_manager = ModelManager()
        self.agent = PatentLocalizationAgent(self.model_manager)
        
        # 创建临时输出目录
        self.temp_dir = Path(tempfile.mkdtemp())
        self.output_dir = self.temp_dir / "patents"
        self.output_dir.mkdir()
    
    def tearDown(self):
        """清理测试环境。"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    async def test_patent_localization_real_url(self):
        """测试真实专利URL的本地化流程。"""
        # 使用真实的专利URL进行测试
        test_url = "https://patents.google.com/patent/CN116555216A/en?oq=CN+116555216+A"
        
        # 运行本地化流程
        result = await self.agent.localize_patent(test_url, self.output_dir)
        
        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)
        self.assertIn("patent_id", result)
        self.assertIn("patent_folder", result)
        
        # 验证专利ID提取
        self.assertEqual(result["patent_id"], "CN116555216A")
        
        # 验证文件夹结构
        patent_folder = Path(result["patent_folder"])
        self.assertTrue(patent_folder.exists())
        self.assertTrue(patent_folder.is_dir())
        
        # 验证images文件夹
        images_folder = patent_folder / "images"
        self.assertTrue(images_folder.exists())
        self.assertTrue(images_folder.is_dir())
        
        # 验证进度文件
        progress_file = patent_folder / "progress.md"
        self.assertTrue(progress_file.exists())
        
        # 验证Markdown文件
        if result["status"] == "success":
            markdown_file = Path(result["markdown_file"])
            self.assertTrue(markdown_file.exists())
            
            # 验证Markdown内容
            markdown_content = markdown_file.read_text(encoding='utf-8')
            self.assertIsInstance(markdown_content, str)
            self.assertGreater(len(markdown_content), 0)
            
            # 验证图片引用
            if result.get("downloaded_images"):
                for img_path in result["downloaded_images"]:
                    self.assertTrue(Path(img_path).exists())
    
    def test_patent_localization_sync_wrapper(self):
        """同步包装器测试。"""
        async def async_test():
            await self.test_patent_localization_real_url()
        
        # 运行异步测试
        asyncio.run(async_test())
    
    async def test_patent_localization_error_handling(self):
        """测试错误处理。"""
        # 使用无效URL测试错误处理
        invalid_url = "https://invalid-url-that-does-not-exist.com/patent/INVALID123"
        
        result = await self.agent.localize_patent(invalid_url, self.output_dir)
        
        # 验证错误处理
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)
        
        # 即使失败也应该有基本的文件夹结构
        if result["status"] == "failed":
            self.assertIn("error", result)
            self.assertIn("patent_folder", result)
    
    async def test_multiple_patents_localization(self):
        """测试多个专利的本地化。"""
        test_urls = [
            "https://patents.google.com/patent/CN116555216A/en",
            "https://patents.google.com/patent/US12345678/en",
        ]
        
        results = []
        for url in test_urls:
            result = await self.agent.localize_patent(url, self.output_dir)
            results.append(result)
        
        # 验证所有结果
        self.assertEqual(len(results), len(test_urls))
        
        for result in results:
            self.assertIsInstance(result, dict)
            self.assertIn("status", result)
            self.assertIn("patent_id", result)
            self.assertIn("patent_folder", result)
        
        # 验证文件夹不重复
        patent_folders = [Path(r["patent_folder"]) for r in results]
        self.assertEqual(len(set(patent_folders)), len(patent_folders))


if __name__ == '__main__':
    # 运行异步测试
    unittest.main()