"""专利信息智能提取工具包。

这是一个基于多Agent系统的专利信息智能提取工具，支持专利网页本地化、
结构化处理和智能问答等功能。
"""

__version__ = "0.1.0"
__author__ = "jieke wu"
__email__ = "jieke.jack.wu@gmail.com"

# 导出主要类和函数
from .core.localization_agent import PatentLocalizationAgent

__all__ = [
    "PatentLocalizationAgent",
]

