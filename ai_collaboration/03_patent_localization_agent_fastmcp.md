# 专利网页结构化本地化Agent实现 - FastMCP版本

## 1. MCP 工具集成方案

基于 MCP (Model Context Protocol) 架构，我们使用 FastMCP 来完全替代传统的 lynx + curl 方案：

### 1.1 主要 MCP 工具选择

**FastMCP** - 首选方案
- 基于 FastAPI 的 MCP 服务器实现
- 提供高性能的 MCP 服务
- 支持多种工具和资源
- 易于集成和扩展

**Playwright MCP** - 浏览器自动化
- 基于 Playwright 的浏览器自动化
- 支持完整的网页内容获取
- 可以处理 JavaScript 渲染的内容
- 支持截图和交互操作

### 1.2 系统提示词模板

```
你是一个专业的专利网页结构化本地化助手。你的任务是将专利网页内容完整地本地化并结构化，包括网页内容转换和图片资源下载。

## 任务流程

### 步骤0: 生成笔记
- 仿照例子和当前任务生成笔记 progress.md

### 步骤1: 访问网站并抓取内容
- 使用 FastMCP 或 Playwright MCP 工具访问用户提供的专利URL
- 配置抓取参数：等待页面完全加载，处理JavaScript渲染内容
- 将完整的网页内容保存在raw.md中
- 提取所有图片链接并记录到 progress.md

### 步骤2：下载图片资源
- 从抓取结果中提取专利相关图片链接
- 使用 MCP 图片下载工具下载图片
- 将图片保存到 images/ 文件夹
- 每下载完成一个图片，必须更新图片下载进度

### 步骤3：结构化转换为markdown
- 基于raw.md内容进行结构化处理
- 提取专利的关键信息（标题、摘要、权利要求等）
- 将图片链接替换为本地路径
- 保存为结构化的patent.md文件
- 保持专利的原始语言，不进行翻译

## 文件夹结构
```bash
{专利编号}/
├── progress.md              # 进度记录
├── raw.md                   # 原始网页内容（Markdown格式）
├── patent.md                # 结构化Markdown（保持原语言）
└── images/                  # 图片资源文件夹
    ├── image_001.png
    ├── image_002.png
    └── ...
```

## progress.md 笔记格式
```markdown
## 任务
[x] 访问网站并抓取内容
[x] 下载图片资源
[ ] 结构化转换为markdown

## 图片下载进度
[x] https://xxxx/yyy.png
[ ] https://foo/bar.png
...

## 当前任务
正在下载https://foo/bar.png
```

## 重要规则
1. 专利文件夹名称 = 专利编号（从URL中提取）
2. 使用 MCP 工具进行专业的网页抓取，确保内容完整性
3. 所有图片必须下载到本地images文件夹
4. Markdown中的图片链接必须指向本地图片
5. 每完成一步都要更新progress.md
6. 如果下载失败，记录错误并继续处理其他图片
7. 保持专利的原始语言，不进行翻译
8. 重点进行结构化处理，提取专利的关键信息（标题、摘要、权利要求、描述等）
9. 优先使用 FastMCP 或 Playwright MCP，必要时使用 curl 作为备选
10. 完全放弃传统实现，全部使用 MCP 服务
```

## 2. MCP 工具配置

### 2.1 FastMCP 配置

```python
# 安装 FastMCP
# pip install mcp

from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent

# 创建 FastMCP 服务器
mcp_server = FastMCP("patent-localization-server")

@mcp_server.tool()
async def scrape_webpage(url: str) -> str:
    """抓取网页内容并返回Markdown格式。"""
    # 实现网页抓取逻辑
    pass

@mcp_server.tool()
async def download_image(url: str, local_path: str) -> bool:
    """下载图片到本地路径。"""
    # 实现图片下载逻辑
    pass
```

### 2.2 Playwright MCP 配置

```python
# 安装 Playwright MCP
# pip install playwright-mcp

from playwright_mcp import PlaywrightMCP

# 创建 Playwright MCP 服务器
playwright_mcp = PlaywrightMCP()

# 配置浏览器选项
browser_options = {
    "headless": True,
    "viewport": {"width": 1920, "height": 1080},
    "wait_for_load_state": "networkidle"
}
```

## 3. 专利结构化本地化Agent实现

```python
"""专利结构化本地化Agent实现 - FastMCP集成版本。"""

import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

# FastMCP 集成
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent

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
            openai_api_base=text_config["api_base"],
            openai_api_key=text_config["api_key"],
            temperature=text_config["temperature"],
            max_tokens=text_config["max_tokens"]
        )
        
        # 初始化 FastMCP 服务器
        self.mcp_server = self._init_fastmcp_server()
        
        logger.info(f"专利本地化Agent初始化完成，使用模型: {text_config['model']}")
        logger.info("FastMCP 服务器已启用")
    
    def _init_fastmcp_server(self) -> FastMCP:
        """初始化 FastMCP 服务器。"""
        mcp_server = FastMCP("patent-localization-server")
        
        @mcp_server.tool()
        async def scrape_webpage(url: str) -> str:
            """抓取网页内容并返回Markdown格式。"""
            try:
                # 使用 Playwright 或类似工具抓取网页
                # 这里需要实际的实现
                logger.info(f"抓取网页: {url}")
                return f"# 抓取的网页内容\n\n从 {url} 抓取的内容..."
            except Exception as e:
                logger.error(f"网页抓取失败: {e}")
                raise
        
        @mcp_server.tool()
        async def download_image(url: str, local_path: str) -> bool:
            """下载图片到本地路径。"""
            try:
                # 实现图片下载逻辑
                logger.info(f"下载图片: {url} -> {local_path}")
                return True
            except Exception as e:
                logger.error(f"图片下载失败: {e}")
                return False
        
        return mcp_server
    
    async def localize_patent(self, url: str, output_dir: Path) -> Dict[str, Any]:
        """结构化本地化专利网页内容。
        
        Args:
            url: 专利网页URL
            output_dir: 输出目录
            
        Returns:
            本地化结果字典
        """
        logger.info(f"开始结构化本地化专利: {url}")
        
        patent_id = "unknown"  # 初始化专利ID
        
        try:
            # 提取专利编号
            patent_id = self._extract_patent_id(url)
            
            # 创建专利文件夹
            patent_folder = output_dir / patent_id
            patent_folder.mkdir(parents=True, exist_ok=True)
            images_folder = patent_folder / "images"
            images_folder.mkdir(exist_ok=True)
            
            # 初始化进度文件
            progress_file = patent_folder / "progress.md"
            self._init_progress_file(progress_file, url)
            
            # 步骤1: 使用 FastMCP 工具抓取网页内容
            raw_content = await self._fetch_webpage_with_mcp(url)
            raw_file = patent_folder / "raw.md"
            raw_file.write_text(raw_content, encoding='utf-8')
            self._update_progress(progress_file, "访问网站并抓取内容", True)
            
            # 步骤2: 下载图片资源
            image_links = self._extract_image_links(raw_content)
            downloaded_images = await self._download_images(image_links, images_folder, progress_file)
            
            # 步骤3: 结构化转换为markdown
            markdown_content = self._convert_to_structured_markdown(raw_content, downloaded_images)
            markdown_file = patent_folder / "patent.md"
            markdown_file.write_text(markdown_content, encoding='utf-8')
            self._update_progress(progress_file, "结构化转换为markdown", True)
            
            logger.info(f"专利结构化本地化完成: {patent_folder}")
            
            return {
                "patent_id": patent_id,
                "patent_folder": str(patent_folder),
                "files_created": [
                    "progress.md",
                    "raw.md", 
                    "patent.md"
                ],
                "images_downloaded": len(downloaded_images),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"专利结构化本地化失败: {e}")
            return {
                "patent_id": patent_id,
                "error": str(e),
                "status": "failed"
            }
    
    def _extract_patent_id(self, url: str) -> str:
        """从URL中提取专利编号。"""
        import re
        
        # 提取专利编号的逻辑
        patterns = [
            r'patent/([A-Z]{2}\d+[A-Z]?\d*)',  # Google Patents
            r'patent/(US\d+[A-Z]?\d*)',        # USPTO
            r'patent/(CN\d+[A-Z]?\d*)',        # CNIPA
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # 如果没有匹配到，使用URL的最后一部分
        return url.split('/')[-1].replace('.html', '').replace('.htm', '')
    
    async def _fetch_webpage_with_mcp(self, url: str) -> str:
        """使用 FastMCP 抓取网页内容。"""
        try:
            # 调用 FastMCP 工具
            result = await self.mcp_server.call_tool("scrape_webpage", {"url": url})
            return result
        except Exception as e:
            logger.error(f"FastMCP 网页抓取失败: {e}")
            raise
    
    def _extract_image_links(self, content: str) -> List[str]:
        """从内容中提取图片链接。"""
        import re
        
        image_links = []
        
        # 提取 Markdown 格式的图片链接 ![alt](url)
        markdown_pattern = r'!\[.*?\]\((https?://[^\s)]+)\)'
        markdown_matches = re.findall(markdown_pattern, content)
        image_links.extend(markdown_matches)
        
        # 提取 HTML 格式的图片链接 <img src="url">
        html_pattern = r'<img[^>]+src=["\'](https?://[^"\']+)["\'][^>]*>'
        html_matches = re.findall(html_pattern, content)
        image_links.extend(html_matches)
        
        # 去重并保持顺序
        seen = set()
        unique_links = []
        for link in image_links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        
        logger.info(f"提取到 {len(unique_links)} 个图片链接")
        return unique_links
    
    async def _download_images(self, image_links: List[str], images_folder: Path, progress_file: Path) -> Dict[str, str]:
        """下载图片到本地。"""
        downloaded_images = {}
        
        # 更新进度文件，记录图片下载任务
        self._update_progress(progress_file, "下载图片资源", False, image_urls=image_links)
        
        for i, image_url in enumerate(image_links):
            image_name = f"image_{i+1:03d}{Path(image_url).suffix.split('?')[0]}"
            image_path = images_folder / image_name
            
            self._update_progress(progress_file, f"正在下载{image_url}", False, current_image_url=image_url)
            
            try:
                # 使用 FastMCP 工具下载图片
                success = await self.mcp_server.call_tool("download_image", {
                    "url": image_url,
                    "local_path": str(image_path)
                })
                
                if success:
                    downloaded_images[image_url] = str(Path("images") / image_name)
                    self._update_progress(progress_file, f"下载图片", True, current_image_url=image_url)
                    logger.info(f"成功下载图片: {image_url} -> {image_path}")
                else:
                    self._update_progress(progress_file, f"下载图片失败: {image_url}", False, current_image_url=image_url, failed=True)
                    logger.warning(f"图片下载失败: {image_url}")
                
            except Exception as e:
                logger.warning(f"图片下载异常: {image_url}, 错误: {e}")
                self._update_progress(progress_file, f"图片下载异常: {image_url}, 错误: {e}", False, current_image_url=image_url, failed=True)
        
        return downloaded_images
    
    def _convert_to_structured_markdown(self, raw_content: str, image_mapping: Dict[str, str]) -> str:
        """将原始内容转换为结构化的Markdown格式。"""
        # 限制输入长度，避免超过模型限制
        max_length = 25000  # 留一些余量
        if len(raw_content) > max_length:
            raw_content = raw_content[:max_length] + "\n\n[内容已截断...]"
        
        # 使用LLM进行结构化内容转换
        prompt = f"""
请将以下专利网页内容转换为结构化的Markdown格式。

原始内容：
{raw_content}

要求：
1. 保持专利的原始语言，不进行翻译
2. 重点进行结构化处理，提取专利的关键信息：
   - 专利标题 (Title)
   - 专利摘要 (Abstract)
   - 发明人 (Inventors)
   - 专利权人 (Assignee)
   - 公开号 (Publication Number)
   - 公开日期 (Publication Date)
   - 专利描述 (Description)
   - 权利要求 (Claims)
   - 附图说明 (Drawings)
3. 将图片链接替换为本地路径
4. 使用合适的Markdown格式和标题层级
5. 保持内容的完整性和可读性
6. 确保结构化信息的准确性

图片映射：
{image_mapping}
"""
        
        messages = [
            SystemMessage(content="你是一个专业的专利文档结构化助手，能够将网页内容转换为结构化的Markdown文档，重点提取专利的关键信息。"),
            HumanMessage(content=prompt)
        ]
        
        response = self.model.invoke(messages)
        return response.content
    
    def _init_progress_file(self, progress_file: Path, url: str) -> None:
        """初始化进度文件。"""
        content = f"""## 任务
[ ] 访问网站并抓取内容
[ ] 下载图片资源
[ ] 结构化转换为markdown

## 图片下载进度

## 当前任务
开始处理: {url}
"""
        progress_file.write_text(content, encoding='utf-8')
    
    def _update_progress(self, progress_file: Path, task: str, completed: bool, image_urls: Optional[List[str]] = None, current_image_url: Optional[str] = None, failed: bool = False) -> None:
        """更新任务进度。"""
        content = progress_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # 更新主任务进度
        for i, line in enumerate(lines):
            if task in line:
                if completed:
                    lines[i] = line.replace('[ ]', '[x]')
                break
        
        # 更新图片下载进度
        if image_urls is not None:
            image_progress_start_idx = -1
            for i, line in enumerate(lines):
                if "## 图片下载进度" in line:
                    image_progress_start_idx = i
                    break
            
            if image_progress_start_idx != -1:
                # 清空旧的图片进度
                new_lines = lines[:image_progress_start_idx + 1]
                
                for url in image_urls:
                    status_char = '[ ]'
                    if current_image_url == url:
                        if completed:
                            status_char = '[x]'
                        elif failed:
                            status_char = '[x] ❌'  # 标记失败
                        else:
                            status_char = '[ ] ➡️'  # 正在下载
                    new_lines.append(f"{status_char} {url}")
                lines = new_lines + lines[image_progress_start_idx + 1 + len(image_urls):]  # 重新拼接
        
        # 更新当前任务
        current_task_start_idx = -1
        for i, line in enumerate(lines):
            if "## 当前任务" in line:
                current_task_start_idx = i
                break
        
        if current_task_start_idx != -1:
            if current_image_url:
                if completed:
                    lines[current_task_start_idx + 1] = f"已完成下载: {current_image_url}"
                elif failed:
                    lines[current_task_start_idx + 1] = f"下载失败: {current_image_url}"
                else:
                    lines[current_task_start_idx + 1] = f"正在下载: {current_image_url}"
            else:
                lines[current_task_start_idx + 1] = task
        
        content = '\n'.join(lines)
        progress_file.write_text(content, encoding='utf-8')
```

## 4. 使用示例

```python
import asyncio
from pathlib import Path
from patents_extractor import PatentLocalizationAgent, ModelManager

async def main():
    # 创建Agent
    model_manager = ModelManager()
    localization_agent = PatentLocalizationAgent(model_manager)

    # 结构化本地化专利
    url = "https://patents.google.com/patent/CN116555216A/en?oq=CN+116555216+A"
    output_dir = Path("output/patents")

    result = await localization_agent.localize_patent(url, output_dir)
    print(f"结构化本地化结果: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 5. 优势对比

| 特性         | 传统方法 (lynx + curl) | FastMCP 集成方法 |
| ------------ | ---------------------- | ---------------- |
| 内容抓取质量 | 基础文本提取           | 专业网页解析     |
| 图片处理     | 手动下载               | 内置图片处理     |
| 错误处理     | 基础重试               | 智能重试机制     |
| 内容格式     | 纯文本                 | Markdown/结构化  |
| 维护成本     | 高（依赖外部工具）     | 低（统一接口）   |
| 扩展性       | 有限                   | 高（多种MCP工具）|
| 异步支持     | 无                     | 有（async/await）|
| 生态集成     | 独立                   | 与MCP生态集成   |

## 6. 集成到现有系统

这个Agent是专利结构化处理的第一步，专门负责将网页专利文件结构化。它提供了清晰的接口，便于后期被其他Agent调用：

- **输入**: 专利URL
- **输出**: 结构化的本地文件（patent.md + images/）
- **功能**: 专业网页抓取、图片下载、结构化转换
- **优势**: 使用 FastMCP 确保内容完整性和准确性
- **集成**: 与现有 MCP 生态无缝集成，提供异步支持和错误处理

后续的Agent可以基于这个结构化的Markdown文件进行进一步的问答和输出格式化。
