# 专利网页结构化本地化Agent实现

## 1. Gemini-CLI 提示词模板

基于您提供的gemini-cli提示词，我设计了专利结构化本地化的System Prompt：

```
你是一个专业的专利网页结构化本地化助手。你的任务是将专利网页内容完整地本地化并结构化，包括网页内容转换和图片资源下载。

## 任务流程

### 步骤0: 生成笔记
- 仿照例子和当前任务生成笔记 progress.md

### 步骤1: 访问网站
- 访问用户提供的专利URL
- 必须使用 "lynx -dump -image_links URL" 命令访问网站
- 网站内容保存在raw.txt中

### 步骤2：下载图片
- 从raw.txt中提取专利相关图片链接
- 把图片链接写入 progress.md
- 逐一下载到 images/ 文件夹
- 每下载完成一个图片，必须更新图片下载进度
- 你必须使用curl命令进行下载

### 步骤3：结构化转换为markdown
- 把raw.txt改写成结构化的markdown格式
- 保存在patent.md中
- 将patent.md中的图片链接指向 images/ 文件夹
- 保持专利的原始语言，不进行翻译

## 文件夹结构
```bash
{专利编号}/
├── progress.md              # 进度记录
├── raw.txt                  # 原始网页内容
├── patent.md                # 结构化Markdown（保持原语言）
└── images/                  # 图片资源文件夹
    ├── image_001.png
    ├── image_002.png
    └── ...
```

## progress.md 笔记格式
```markdown
## 任务
[x] 访问网站
[x] 下载图片
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
2. 所有图片必须下载到本地images文件夹
3. Markdown中的图片链接必须指向本地图片
4. 每完成一步都要更新progress.md
5. 如果下载失败，记录错误并继续处理其他图片
6. 保持专利的原始语言，不进行翻译
7. 重点进行结构化处理，提取专利的关键信息（标题、摘要、权利要求、描述等）
```

## 2. 专利结构化本地化Agent实现

```python
"""专利结构化本地化Agent实现。"""

import logging
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..models.config import ModelManager


logger = logging.getLogger(__name__)


class PatentLocalizationAgent:
    """专利结构化本地化Agent。
    
    负责将专利网页内容完整本地化并结构化，包括内容转换和图片下载。
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
        
        logger.info(f"专利本地化Agent初始化完成，使用模型: {text_config['model']}")
    
    def localize_patent(self, url: str, output_dir: Path) -> Dict[str, Any]:
        """结构化本地化专利网页内容。
        
        Args:
            url: 专利网页URL
            output_dir: 输出目录
            
        Returns:
            本地化结果字典
        """
        logger.info(f"开始结构化本地化专利: {url}")
        
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
            
            # 步骤1: 访问网站
            raw_content = self._fetch_webpage_content(url)
            raw_file = patent_folder / "raw.txt"
            raw_file.write_text(raw_content, encoding='utf-8')
            self._update_progress(progress_file, "访问网站", True)
            
            # 步骤2: 下载图片
            image_links = self._extract_image_links(raw_content)
            downloaded_images = self._download_images(image_links, images_folder, progress_file)
            
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
                    "raw.txt", 
                    "patent.md"
                ],
                "images_downloaded": len(downloaded_images),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"专利结构化本地化失败: {e}")
            return {
                "patent_id": patent_id if 'patent_id' in locals() else "unknown",
                "error": str(e),
                "status": "failed"
            }
    
    def _extract_patent_id(self, url: str) -> str:
        """从URL中提取专利编号。"""
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
    
    def _fetch_webpage_content(self, url: str) -> str:
        """使用lynx获取网页内容。"""
        try:
            result = subprocess.run(
                ["lynx", "-dump", "-image_links", url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"lynx命令执行失败: {result.stderr}")
            
            return result.stdout
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("网页访问超时")
        except FileNotFoundError:
            raise RuntimeError("lynx工具未安装")
    
    def _extract_image_links(self, content: str) -> List[str]:
        """从lynx输出中提取图片链接。"""
        image_links = []
        lines = content.split('\n')
        
        for line in lines:
            # lynx输出的图片链接格式
            if 'IMAGE:' in line:
                # 提取图片URL
                url_match = re.search(r'https?://[^\s]+', line)
                if url_match:
                    image_links.append(url_match.group())
        
        return image_links
    
    def _download_images(self, image_links: List[str], images_folder: Path, progress_file: Path) -> Dict[str, str]:
        """下载图片到本地。"""
        downloaded_images = {}
        
        for i, image_url in enumerate(image_links):
            try:
                # 生成本地文件名
                local_filename = f"image_{i+1:03d}.png"
                local_path = images_folder / local_filename
                
                # 使用curl下载图片
                result = subprocess.run(
                    ["curl", "-o", str(local_path), image_url],
                    capture_output=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    downloaded_images[image_url] = str(local_path)
                    logger.info(f"图片下载成功: {local_filename}")
                else:
                    logger.warning(f"图片下载失败: {image_url}")
                
                # 更新进度
                self._update_image_progress(progress_file, image_url, result.returncode == 0)
                
            except subprocess.TimeoutExpired:
                logger.warning(f"图片下载超时: {image_url}")
            except Exception as e:
                logger.warning(f"图片下载异常: {image_url}, 错误: {e}")
        
        return downloaded_images
    
    def _convert_to_structured_markdown(self, raw_content: str, image_mapping: Dict[str, str]) -> str:
        """将原始内容转换为结构化的Markdown格式。"""
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
[ ] 访问网站
[ ] 下载图片
[ ] 结构化转换为markdown

## 图片下载进度

## 当前任务
开始处理: {url}
"""
        progress_file.write_text(content, encoding='utf-8')
    
    def _update_progress(self, progress_file: Path, task: str, completed: bool) -> None:
        """更新任务进度。"""
        content = progress_file.read_text(encoding='utf-8')
        
        # 更新任务状态
        if completed:
            content = content.replace(f"[ ] {task}", f"[x] {task}")
        else:
            content = content.replace(f"[x] {task}", f"[ ] {task}")
        
        progress_file.write_text(content, encoding='utf-8')
    
    def _update_image_progress(self, progress_file: Path, image_url: str, completed: bool) -> None:
        """更新图片下载进度。"""
        content = progress_file.read_text(encoding='utf-8')
        
        # 添加图片下载记录
        status = "[x]" if completed else "[ ]"
        image_line = f"{status} {image_url}\n"
        
        # 在图片下载进度部分添加
        if "## 图片下载进度" in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line == "## 图片下载进度":
                    lines.insert(i + 1, image_line)
                    break
            content = '\n'.join(lines)
        
        progress_file.write_text(content, encoding='utf-8')
```

## 3. 使用示例

```python
# 创建Agent
model_manager = ModelManager()
localization_agent = PatentLocalizationAgent(model_manager)

# 结构化本地化专利
url = "https://patents.google.com/patent/US12345678"
output_dir = Path("output/patents")

result = localization_agent.localize_patent(url, output_dir)
print(f"结构化本地化结果: {result}")
```

## 4. 集成到现有系统

这个Agent是专利结构化处理的第一步，专门负责将网页专利文件结构化。它提供了清晰的接口，便于后期被其他Agent调用：

- **输入**: 专利URL
- **输出**: 结构化的本地文件（patent.md + images/）
- **功能**: 网页内容获取、图片下载、结构化转换

后续的Agent可以基于这个结构化的Markdown文件进行进一步的问答和输出格式化。
