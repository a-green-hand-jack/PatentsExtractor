"""测试结构化Agent。"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from patents_extractor.agents.structured_agent import StructuredAgent
from patents_extractor.models.patent import PatentDocument


class TestStructuredAgent:
    """结构化Agent测试类。"""
    
    def setup_method(self):
        """测试前准备。"""
        self.agent = StructuredAgent()
    
    def test_init(self):
        """测试初始化。"""
        assert self.agent is not None
        assert self.agent.file_processor is not None
        assert self.agent.web_processor is not None
        assert self.agent.pdf_processor is not None
    
    def test_is_url(self):
        """测试URL判断。"""
        assert self.agent._is_url("https://patents.google.com/patent/US12345678")
        assert self.agent._is_url("http://example.com")
        assert not self.agent._is_url("not_a_url")
        assert not self.agent._is_url("file.pdf")
    
    def test_is_pdf_file(self):
        """测试PDF文件判断。"""
        # 创建临时PDF文件
        temp_pdf = Path("temp_test.pdf")
        temp_pdf.touch()
        
        try:
            assert self.agent._is_pdf_file("temp_test.pdf")
            assert not self.agent._is_pdf_file("not_exist.pdf")
            assert not self.agent._is_pdf_file("file.txt")
        finally:
            temp_pdf.unlink()
    
    @patch('patents_extractor.agents.structured_agent.WebProcessor')
    def test_process_web(self, mock_web_processor):
        """测试网页处理。"""
        # 模拟网页处理器
        mock_processor = Mock()
        mock_processor.extract_content.return_value = {
            "title": "Test Patent",
            "abstract": "Test abstract",
            "inventors": ["John Doe"],
            "assignee": "Test Company",
            "publication_number": "US12345678",
            "description": "Test description",
            "claims": "Test claims",
            "drawings": []
        }
        mock_web_processor.return_value = mock_processor
        
        # 重新初始化agent以使用mock
        agent = StructuredAgent()
        agent.web_processor = mock_processor
        
        result = agent._process_web("https://patents.google.com/patent/US12345678")
        
        assert isinstance(result, PatentDocument)
        assert result.title == "Test Patent"
        assert result.source_type == "web"
    
    @patch('patents_extractor.agents.structured_agent.PDFProcessor')
    def test_process_pdf(self, mock_pdf_processor):
        """测试PDF处理。"""
        # 模拟PDF处理器
        mock_processor = Mock()
        mock_processor.extract_content.return_value = {
            "title": "Test Patent PDF",
            "abstract": "Test abstract from PDF",
            "inventors": ["Jane Doe"],
            "assignee": "Test Company PDF",
            "publication_number": "US87654321",
            "description": "Test description from PDF",
            "claims": "Test claims from PDF",
            "drawings": []
        }
        mock_pdf_processor.return_value = mock_processor
        
        # 重新初始化agent以使用mock
        agent = StructuredAgent()
        agent.pdf_processor = mock_processor
        
        result = agent._process_pdf("test_patent.pdf")
        
        assert isinstance(result, PatentDocument)
        assert result.title == "Test Patent PDF"
        assert result.source_type == "pdf"
    
    def test_process_invalid_input(self):
        """测试无效输入。"""
        with pytest.raises(ValueError):
            self.agent.process("invalid_input")
