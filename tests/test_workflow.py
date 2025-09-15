"""测试基于LangGraph的专利提取工作流。"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from patents_extractor.core.workflow import PatentExtractionWorkflow
from patents_extractor.models.state import PatentExtractionState
from patents_extractor.models.patent import PatentQuery


class TestPatentExtractionWorkflow:
    """专利提取工作流测试类。"""
    
    def setup_method(self):
        """测试前准备。"""
        self.workflow = PatentExtractionWorkflow()
    
    def test_init(self):
        """测试初始化。"""
        assert self.workflow is not None
        assert self.workflow.model_name == "gpt-4"
        assert self.workflow.graph is not None
        assert self.workflow.structured_node is not None
        assert self.workflow.qa_node is not None
        assert self.workflow.output_node is not None
    
    @patch('patents_extractor.agents.structured_node.WebProcessor')
    @patch('patents_extractor.agents.qa_node.ChatOpenAI')
    def test_extract_web_success(self, mock_chat_openai, mock_web_processor):
        """测试网页提取成功场景。"""
        # 模拟网页处理器
        mock_web_processor.return_value.extract_content.return_value = {
            "title": "Test Patent",
            "abstract": "Test abstract",
            "inventors": ["John Doe"],
            "assignee": "Test Company",
            "publication_number": "US12345678",
            "description": "Test description",
            "claims": "Test claims",
            "drawings": [],
            "raw_text": "Test raw text"
        }
        
        # 模拟ChatOpenAI
        mock_response = Mock()
        mock_response.content = "This is a test answer about the patent."
        mock_chat_openai.return_value.invoke.return_value = mock_response
        
        # 执行提取
        result = self.workflow.extract(
            input_source="https://patents.google.com/patent/US12345678",
            question="What is this patent about?",
            output_format="both"
        )
        
        # 验证结果
        assert result["answer"] == "This is a test answer about the patent."
        assert result["confidence_score"] > 0
        assert result["markdown_output"] != ""
        assert result["json_output"] != ""
        assert result["processing_time"] > 0
        assert result["model_used"] == "gpt-4"
        assert result["error_message"] is None
    
    @patch('patents_extractor.agents.structured_node.PDFProcessor')
    @patch('patents_extractor.agents.qa_node.ChatOpenAI')
    def test_extract_pdf_success(self, mock_chat_openai, mock_pdf_processor):
        """测试PDF提取成功场景。"""
        # 创建临时PDF文件
        temp_pdf = Path("temp_test.pdf")
        temp_pdf.touch()
        
        try:
            # 模拟PDF处理器
            mock_pdf_processor.return_value.extract_content.return_value = {
                "title": "Test PDF Patent",
                "abstract": "Test PDF abstract",
                "inventors": ["Jane Doe"],
                "assignee": "Test PDF Company",
                "publication_number": "US87654321",
                "description": "Test PDF description",
                "claims": "Test PDF claims",
                "drawings": [],
                "raw_text": "Test PDF raw text"
            }
            
            # 模拟ChatOpenAI
            mock_response = Mock()
            mock_response.content = "This is a test answer about the PDF patent."
            mock_chat_openai.return_value.invoke.return_value = mock_response
            
            # 执行提取
            result = self.workflow.extract(
                input_source="temp_test.pdf",
                question="What are the main claims?",
                output_format="markdown"
            )
            
            # 验证结果
            assert result["answer"] == "This is a test answer about the PDF patent."
            assert result["confidence_score"] > 0
            assert result["markdown_output"] != ""
            assert result["json_output"] == ""  # 只要求markdown格式
            assert result["processing_time"] > 0
            assert result["error_message"] is None
            
        finally:
            temp_pdf.unlink()
    
    def test_extract_invalid_input(self):
        """测试无效输入。"""
        result = self.workflow.extract(
            input_source="invalid_input",
            question="Test question",
            output_format="both"
        )
        
        assert result["answer"] == ""
        assert result["confidence_score"] == 0.0
        assert result["error_message"] is not None
    
    @patch('patents_extractor.agents.structured_node.WebProcessor')
    def test_extract_web_processing_error(self, mock_web_processor):
        """测试网页处理错误。"""
        # 模拟网页处理器抛出异常
        mock_web_processor.return_value.extract_content.side_effect = Exception("Web processing failed")
        
        result = self.workflow.extract(
            input_source="https://patents.google.com/patent/US12345678",
            question="Test question",
            output_format="both"
        )
        
        assert result["answer"] == ""
        assert result["error_message"] == "Web processing failed"
    
    def test_get_workflow_status(self):
        """测试获取工作流状态。"""
        status = self.workflow.get_workflow_status("test_thread")
        
        assert "current_step" in status
        assert "completed_steps" in status
        assert "next_step" in status
        assert "error_message" in status
        assert "is_complete" in status
        assert "is_error" in status
