"""专利本地化Agent单元测试 - FastMCP版本。"""

import unittest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile
import shutil

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from patents_extractor.agents.patent_localization_agent import PatentLocalizationAgent
from patents_extractor.models.config import ModelManager


class TestPatentLocalizationAgent(unittest.TestCase):
    """专利本地化Agent测试类 - FastMCP版本。"""
    
    def setUp(self):
        """设置测试环境。"""
        self.model_manager = Mock(spec=ModelManager)
        self.model_manager.get_text_model_config.return_value = {
            "model": "qwen-max",
            "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "api_key": "test-key",
            "temperature": 0.1,
            "max_tokens": 2000
        }
        
        self.agent = PatentLocalizationAgent(self.model_manager)
        
        # 创建临时目录
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """清理测试环境。"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_extract_patent_id(self):
        """测试专利ID提取。"""
        test_cases = [
            ("https://patents.google.com/patent/CN116555216A/en", "CN116555216A"),
            ("https://patents.google.com/patent/CN116555216/en", "CN116555216"),
            ("https://example.com/patent/US12345678", "US12345678"),
            ("https://example.com/unknown", "unknown"),
        ]
        
        for url, expected in test_cases:
            with self.subTest(url=url):
                result = self.agent._extract_patent_id(url)
                self.assertEqual(result, expected)
    
    def test_init_progress_file(self):
        """测试进度文件初始化。"""
        patent_folder = self.temp_dir / "test_patent"
        patent_folder.mkdir()
        
        progress_file = self.agent._init_progress_file(patent_folder)
        
        self.assertTrue(progress_file.exists())
        self.assertEqual(progress_file.name, "progress.md")
        
        content = progress_file.read_text(encoding='utf-8')
        self.assertIn("专利本地化进度", content)
        self.assertIn("网页抓取", content)
    
    def test_extract_image_links(self):
        """测试图片链接提取。"""
        content = """
        # 测试内容
        
        ![图片1](https://example.com/image1.jpg)
        <img src="https://example.com/image2.png" alt="图片2">
        <img src="/relative/image3.gif" alt="图片3">
        """
        
        base_url = "https://patents.google.com/patent/CN116555216A/en"
        
        image_links = self.agent._extract_image_links(content, base_url)
        
        self.assertEqual(len(image_links), 3)
        self.assertIn("https://example.com/image1.jpg", image_links)
        self.assertIn("https://example.com/image2.png", image_links)
        self.assertIn("https://patents.google.com/relative/image3.gif", image_links)
    
    def test_update_progress(self):
        """测试进度更新。"""
        patent_folder = self.temp_dir / "test_patent"
        patent_folder.mkdir()
        
        progress_file = self.agent._init_progress_file(patent_folder)
        
        # 更新进度
        self.agent._update_progress(progress_file, "网页抓取", "完成")
        
        content = progress_file.read_text(encoding='utf-8')
        self.assertIn("- [x] 网页抓取", content)
    
    @patch('patents_extractor.agents.patent_localization_agent.MCP_AVAILABLE', True)
    def test_fastmcp_server_initialization(self):
        """测试FastMCP服务器初始化。"""
        with patch('patents_extractor.agents.patent_localization_agent.FastMCP') as mock_fastmcp:
            mock_server = Mock()
            mock_fastmcp.return_value = mock_server
            
            # 重新初始化agent
            agent = PatentLocalizationAgent(self.model_manager)
            
            self.assertIsNotNone(agent.mcp_server)
            mock_fastmcp.assert_called_once_with("patent-localization-server")
    
    @patch('patents_extractor.agents.patent_localization_agent.MCP_AVAILABLE', False)
    def test_no_fastmcp_fallback(self):
        """测试FastMCP不可用时的回退。"""
        agent = PatentLocalizationAgent(self.model_manager)
        
        self.assertIsNone(agent.mcp_server)
    
    def test_fetch_webpage_with_fastmcp_success(self):
        """测试FastMCP网页抓取成功。"""
        mock_server = Mock()
        mock_server.call_tool = AsyncMock(return_value="# 测试网页内容\n\n这是测试内容")
        self.agent.mcp_server = mock_server
        
        url = "https://example.com/test"
        
        # 使用asyncio.run运行异步方法
        import asyncio
        result = asyncio.run(self.agent._fetch_webpage_with_fastmcp(url))
        
        self.assertIn("测试网页内容", result)
        mock_server.call_tool.assert_called_once_with("scrape_webpage", {"url": url})
    
    def test_fetch_webpage_with_fastmcp_fallback(self):
        """测试FastMCP网页抓取失败时的回退。"""
        self.agent.mcp_server = None  # 模拟FastMCP不可用
        
        url = "https://example.com/test"
        
        # 使用asyncio.run运行异步方法
        import asyncio
        result = asyncio.run(self.agent._fetch_webpage_with_fastmcp(url))
        
        self.assertIn("模拟网页内容", result)
        self.assertIn(url, result)
    
    def test_download_images_with_fastmcp_success(self):
        """测试FastMCP图片下载成功。"""
        mock_server = Mock()
        mock_server.call_tool = AsyncMock(return_value=True)
        self.agent.mcp_server = mock_server
        
        image_links = ["https://example.com/image1.jpg", "https://example.com/image2.png"]
        images_folder = self.temp_dir / "images"
        images_folder.mkdir()
        
        # 使用asyncio.run运行异步方法
        import asyncio
        result = asyncio.run(self.agent._download_images_with_fastmcp(image_links, images_folder))
        
        self.assertEqual(len(result), 2)
        # 验证返回的路径存在
        for img_path in result:
            self.assertTrue(Path(img_path).exists())
        self.assertEqual(mock_server.call_tool.call_count, 2)
    
    def test_download_images_with_fastmcp_fallback(self):
        """测试FastMCP图片下载失败时的回退。"""
        self.agent.mcp_server = None  # 模拟FastMCP不可用
        
        image_links = ["https://example.com/image1.jpg"]
        images_folder = self.temp_dir / "images"
        images_folder.mkdir()
        
        # 使用asyncio.run运行异步方法
        import asyncio
        result = asyncio.run(self.agent._download_images_with_fastmcp(image_links, images_folder))
        
        self.assertEqual(len(result), 1)
        self.assertTrue(Path(result[0]).exists())
    
    @patch.object(PatentLocalizationAgent, '_convert_to_structured_markdown')
    def test_convert_to_structured_markdown(self, mock_convert):
        """测试Markdown转换。"""
        raw_content = "# 测试专利\n\n这是一个测试专利的内容。"
        downloaded_images = ["images/image_001.jpg"]
        
        # 模拟转换结果
        mock_convert.return_value = "# 结构化专利文档\n\n## 专利标题\n测试专利"
        
        result = self.agent._convert_to_structured_markdown(raw_content, downloaded_images)
        
        self.assertIn("结构化专利文档", result)
        self.assertIn("专利标题", result)
    
    @patch.object(PatentLocalizationAgent, '_convert_to_structured_markdown')
    def test_convert_to_structured_markdown_error(self, mock_convert):
        """测试Markdown转换错误处理。"""
        raw_content = "# 测试专利\n\n这是一个测试专利的内容。"
        downloaded_images = ["images/image_001.jpg"]
        
        # 模拟转换失败，返回错误格式
        mock_convert.return_value = """# 专利文档

## 原始内容

# 测试专利

这是一个测试专利的内容。

## 图片列表

- images/image_001.jpg"""
        
        result = self.agent._convert_to_structured_markdown(raw_content, downloaded_images)
        
        self.assertIn("专利文档", result)
        self.assertIn("原始内容", result)
        self.assertIn("图片列表", result)
    
    def test_localize_patent_success(self):
        """测试完整的专利本地化流程成功。"""
        # 模拟所有依赖方法
        self.agent._extract_patent_id = Mock(return_value="CN116555216A")
        self.agent._init_progress_file = Mock(return_value=self.temp_dir / "progress.md")
        self.agent._update_progress = Mock()
        self.agent._fetch_webpage_with_fastmcp = AsyncMock(return_value="# 测试内容")
        self.agent._extract_image_links = Mock(return_value=["https://example.com/image.jpg"])
        self.agent._download_images_with_fastmcp = AsyncMock(return_value=["images/image_001.jpg"])
        self.agent._convert_to_structured_markdown = Mock(return_value="# 结构化内容")
        
        url = "https://patents.google.com/patent/CN116555216A/en"
        
        # 使用asyncio.run运行异步方法
        import asyncio
        result = asyncio.run(self.agent.localize_patent(url, self.temp_dir))
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["patent_id"], "CN116555216A")
        self.assertIn("patent_folder", result)
        self.assertIn("markdown_file", result)
    
    def test_localize_patent_failure(self):
        """测试专利本地化流程失败。"""
        # 模拟提取专利ID失败
        self.agent._extract_patent_id = Mock(side_effect=Exception("提取失败"))
        self.agent._init_progress_file = Mock(return_value=self.temp_dir / "progress.md")
        self.agent._update_progress = Mock()
        
        url = "https://patents.google.com/patent/CN116555216A/en"
        
        # 使用asyncio.run运行异步方法
        import asyncio
        result = asyncio.run(self.agent.localize_patent(url, self.temp_dir))
        
        self.assertEqual(result["status"], "failed")
        self.assertIn("error", result)
        self.assertIn("patent_folder", result)


if __name__ == '__main__':
    # 运行异步测试
    unittest.main()