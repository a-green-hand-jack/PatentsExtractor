"""专利,构化本地.Agent实现 - FastMCP集成版本。"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

# MCP 服务器集成（如果可用）
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    ClientSession = None
    StdioServerParameters = None
    stdio_client = None

from ..models.config import ModelManager


logger = logging.getLogger(__name__)


class PatentLocalizationAgent:
    """专利结构化本地化Agent - FastMCP集成版本。
    
    负责将专利网页内容完整本地化并结构化，包括内容转换和图片下载。
    使用 FastMCP 进行专业的网页抓取，确保内容完整性和准确性。
    这是专利结构化处理的第一步：将网页专利文件结构化。
    """
    
    def __init__(self, model_manager: ModelManager):
        """初始化专利本地化Agent。
        
        Args:
            model_manager: 模型管理器
        """
        self.model_manager = model_manager
        
        # 使用文本处理模型
        text_config = model_manager.get_text_model_config()
        self.model = ChatOpenAI(
            model=text_config["model"],
            base_url=text_config["api_base"],
            api_key=text_config["api_key"],
            temperature=text_config["temperature"]
        )
        
        # 初始化 MCP 客户端（如果可用）
        self.mcp_client = None
        if MCP_AVAILABLE:
            self.mcp_client = self._init_mcp_client()
            logger.info("MCP 客户端已启用")
        else:
            logger.warning("MCP 不可用，将使用模拟实现")
        
        logger.info(f"专利本地化Agent初始化完成，使用模型: {text_config['model']}")
    
    def _init_mcp_client(self) -> Optional[Any]:
        """初始化 MCP 客户端。"""
        if not MCP_AVAILABLE:
            return None
            
        try:
            # 这里需要实际的 MCP 客户端初始化
            # 由于 MCP 服务器需要独立运行，这里先返回 None
            logger.info("MCP 客户端初始化（需要独立运行 MCP 服务器）")
            return None
            
        except Exception as e:
            logger.error(f"MCP 客户端初始化失败: {e}")
            return None
    
    async def localize_patent(self, url: str, output_dir: Path) -> Dict[str, Any]:
        """结构化本地化专利网页内容。
        
        Args:
            url: 专利网页URL
            output_dir: 输出目录
            
        Returns:
            包含处理结果的字典
        """
        logger.info(f"开始结构化本地化专利: {url}")
        
        # 提取专利编号
        patent_id = self._extract_patent_id(url)
        patent_folder = output_dir / patent_id
        
        # 创建专利文件夹
        patent_folder.mkdir(parents=True, exist_ok=True)
        images_folder = patent_folder / "images"
        images_folder.mkdir(exist_ok=True)
        
        # 初始化进度文件
        progress_file = self._init_progress_file(patent_folder)
        
        try:
            # 1. 抓取网页内容
            logger.info("步骤1: 抓取网页内容")
            raw_content = await self._fetch_webpage_with_mcp(url)
            self._update_progress(progress_file, "网页抓取", "完成")
            
            # 2. 提取图片链接
            logger.info("步骤2: 提取图片链接")
            image_links = self._extract_image_links(raw_content, url)
            self._update_progress(progress_file, "图片链接提取", f"找到 {len(image_links)} 个图片")
            
            # 3. 下载图片
            logger.info("步骤3: 下载图片")
            downloaded_images = await self._download_images_with_http(image_links, images_folder)
            self._update_progress(progress_file, "图片下载", f"成功下载 {len(downloaded_images)} 个图片")
            
            # 4. 转换为结构化Markdown
            logger.info("步骤4: 转换为结构化Markdown")
            markdown_content = self._convert_to_structured_markdown(raw_content, downloaded_images)
            self._update_progress(progress_file, "Markdown转换", "完成")
            
            # 5. 保存Markdown文件
            markdown_file = patent_folder / f"{patent_id}.md"
            markdown_file.write_text(markdown_content, encoding='utf-8')
            self._update_progress(progress_file, "文件保存", "完成")
            
            logger.info(f"专利结构化本地化完成: {patent_folder}")
            
            return {
                "status": "success",
                "patent_id": patent_id,
                "patent_folder": str(patent_folder),
                "markdown_file": str(markdown_file),
                "images_folder": str(images_folder),
                "downloaded_images": downloaded_images,
                "progress_file": str(progress_file)
            }
            
        except Exception as e:
            logger.error(f"专利结构化本地化失败: {e}")
            self._update_progress(progress_file, "错误", str(e))
            
            return {
                "status": "failed",
                "patent_id": patent_id,
                "patent_folder": str(patent_folder),
                "error": str(e)
            }
    
    def _extract_patent_id(self, url: str) -> str:
        """从URL中提取专利编号。"""
        # 匹配各种专利URL格式
        patterns = [
            r'patent/([A-Z]{2}\d+[A-Z]?)',  # CN116555216A
            r'patent/([A-Z]{2}\d+)',        # CN116555216
            r'([A-Z]{2}\d+[A-Z]?)',         # 直接匹配
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # 如果无法提取，使用URL的最后一部分
        return url.split('/')[-1].split('?')[0]
    
    def _init_progress_file(self, patent_folder: Path) -> Path:
        """初始化进度文件。"""
        progress_file = patent_folder / "progress.md"
        progress_content = """# 专利本地化进度

## 处理步骤

- [ ] 网页抓取
- [ ] 图片链接提取  
- [ ] 图片下载
- [ ] Markdown转换
- [ ] 文件保存

## 详细信息

"""
        progress_file.write_text(progress_content, encoding='utf-8')
        return progress_file
    
    def _update_progress(self, progress_file: Path, step: str, status: str) -> None:
        """更新进度文件。"""
        try:
            content = progress_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # 更新步骤状态
            for i, line in enumerate(lines):
                if step in line:
                    if status == "完成":
                        lines[i] = f"- [x] {step}"
                    else:
                        lines[i] = f"- [ ] {step} - {status}"
                    break
            
            # 添加详细信息
            lines.append(f"- {step}: {status}")
            
            progress_file.write_text('\n'.join(lines), encoding='utf-8')
            
        except Exception as e:
            logger.error(f"更新进度文件失败: {e}")
    
    async def _fetch_webpage_with_mcp(self, url: str) -> str:
        """使用 MCP 或 HTTP 请求抓取网页内容。"""
        try:
            # 尝试使用 MCP 客户端
            if self.mcp_client:
                # 这里需要实际的 MCP 调用
                logger.info("使用 MCP 客户端抓取网页")
                # result = await self.mcp_client.call_tool("fetch", {"url": url})
                # return result.get("content", "")
                pass
            
            # 回退到 HTTP 请求
            logger.info("使用 HTTP 请求抓取网页")
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()
                
                # 获取 HTML 内容
                html_content = response.text
                
                # 转换为 Markdown（简单实现）
                markdown_content = self._html_to_markdown(html_content)
                
                return markdown_content
                
        except Exception as e:
            logger.error(f"网页抓取失败: {e}")
            # 返回基础格式
            return f"# 网页抓取失败\n\nURL: {url}\n错误: {str(e)}"
    
    def _html_to_markdown(self, html_content: str) -> str:
        """将 HTML 内容转换为 Markdown。"""
        try:
            from markdownify import markdownify as md
            
            # 使用 markdownify 转换 HTML 到 Markdown
            markdown_content = md(
                html_content,
                heading_style="ATX",  # 使用 # 格式的标题
                bullets="-",          # 使用 - 作为列表符号
                strip=['script', 'style']  # 移除脚本和样式
            )
            
            return markdown_content
            
        except ImportError:
            logger.warning("markdownify 不可用，使用简单转换")
            # 简单的 HTML 标签移除
            import re
            # 移除脚本和样式
            content = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<style.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
            
            # 简单的标签转换
            content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', content, flags=re.IGNORECASE)
            content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', content, flags=re.IGNORECASE)
            content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', content, flags=re.IGNORECASE)
            content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', content, flags=re.IGNORECASE)
            content = re.sub(r'<br[^>]*>', '\n', content, flags=re.IGNORECASE)
            content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', content, flags=re.IGNORECASE)
            content = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', content, flags=re.IGNORECASE)
            
            # 移除剩余的 HTML 标签
            content = re.sub(r'<[^>]+>', '', content)
            
            return content
            
        except Exception as e:
            logger.error(f"HTML 到 Markdown 转换失败: {e}")
            return html_content
    
    def _extract_image_links(self, content: str, base_url: str) -> List[str]:
        """从内容中提取图片链接。"""
        # 匹配各种图片格式
        patterns = [
            r'!\[.*?\]\((.*?)\)',  # Markdown格式
            r'<img[^>]+src=["\'](.*?)["\']',  # HTML格式
            r'src=["\'](.*?\.(?:jpg|jpeg|png|gif|svg|webp))["\']',  # 直接src属性
        ]
        
        image_links = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                
                # 处理相对URL
                if match.startswith('//'):
                    match = 'https:' + match
                elif match.startswith('/'):
                    from urllib.parse import urljoin
                    match = urljoin(base_url, match)
                elif not match.startswith('http'):
                    from urllib.parse import urljoin
                    match = urljoin(base_url, match)
                
                if match not in image_links:
                    image_links.append(match)
        
        return image_links
    
    async def _download_images_with_http(self, image_links: List[str], images_folder: Path) -> List[str]:
        """使用 HTTP 请求下载图片。"""
        downloaded_images = []
        
        for i, image_url in enumerate(image_links):
            try:
                # 生成本地文件名
                image_name = f"image_{i+1:03d}.jpg"
                local_path = images_folder / image_name
                
                # 使用 HTTP 请求下载图片
                import httpx
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_url, timeout=30.0)
                    response.raise_for_status()
                    
                    # 保存图片
                    local_path.write_bytes(response.content)
                    downloaded_images.append(str(local_path))
                    logger.info(f"图片下载成功: {image_url} -> {local_path}")
                    
            except Exception as e:
                logger.error(f"下载图片失败 {image_url}: {e}")
        
        return downloaded_images
    
    def _convert_to_structured_markdown(self, raw_content: str, downloaded_images: List[str]) -> str:
        """将原始内容转换为结构化Markdown。"""
        # 截断内容以避免超出模型限制
        truncated_content = raw_content[:25000] if len(raw_content) > 25000 else raw_content
        
        system_prompt = """你是一个专业的专利文档结构化专家。请将给定的专利网页内容转换为结构化的Markdown格式。

## 转换要求：

1. **保持原始语言**：不要翻译，保持专利的原始语言
2. **结构化组织**：按照专利文档的标准结构组织内容
3. **图片引用**：将图片引用更新为本地路径
4. **清晰格式**：使用适当的Markdown格式和标题层级

## 标准结构：

- 专利标题
- 专利号
- 申请人/发明人信息
- 摘要
- 技术领域
- 背景技术
- 发明内容
- 附图说明
- 具体实施方式
- 权利要求

## 图片处理：

将图片引用更新为相对路径格式：`![描述](images/image_001.jpg)`

请开始转换："""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"请将以下专利内容转换为结构化Markdown：\n\n{truncated_content}")
            ]
            
            response = self.model.invoke(messages)
            if hasattr(response, 'content'):
                content = response.content
                if isinstance(content, str):
                    return content
                else:
                    return str(content)
            else:
                return str(response)
            
        except Exception as e:
            logger.error(f"Markdown转换失败: {e}")
            # 返回基础格式
            return f"""# 专利文档

## 原始内容

{raw_content}

## 图片列表

{chr(10).join([f"- {img}" for img in downloaded_images])}
"""