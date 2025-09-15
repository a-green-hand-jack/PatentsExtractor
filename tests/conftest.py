"""Pytest全局配置和fixtures。"""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """创建临时目录用于测试。"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_pdf_path():
    """示例PDF文件路径。"""
    return Path(__file__).parent / "fixtures" / "sample.pdf"


@pytest.fixture
def sample_html_path():
    """示例HTML文件路径。"""
    return Path(__file__).parent / "fixtures" / "sample.html"


@pytest.fixture
def sample_patent_url():
    """示例专利URL。"""
    return "https://patents.google.com/patent/US12345678"
