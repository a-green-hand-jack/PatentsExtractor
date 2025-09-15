"""文件处理工具。"""

import logging
from pathlib import Path
from typing import Dict, Any


logger = logging.getLogger(__name__)


class FileProcessor:
    """文件处理工具类。
    
    提供通用的文件操作功能。
    """
    
    def __init__(self) -> None:
        """初始化文件处理器。"""
        logger.info("文件处理器初始化完成")
    
    def read_file(self, file_path: Path) -> str:
        """读取文件内容。
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"读取文件失败: {file_path}, 错误: {e}")
            raise
    
    def write_file(self, file_path: Path, content: str) -> None:
        """写入文件内容。
        
        Args:
            file_path: 文件路径
            content: 文件内容
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logger.error(f"写入文件失败: {file_path}, 错误: {e}")
            raise
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """获取文件信息。
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典
        """
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        stat = file_path.stat()
        return {
            "name": file_path.name,
            "size": stat.st_size,
            "extension": file_path.suffix,
            "modified_time": stat.st_mtime,
            "is_file": file_path.is_file(),
            "is_dir": file_path.is_dir()
        }
