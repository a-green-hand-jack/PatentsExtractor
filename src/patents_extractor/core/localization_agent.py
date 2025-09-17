"""专利本地化Agent - 简化版本。

负责将专利网页内容完整本地化并结构化，包括内容转换和图片下载。
使用MarkItDown + requests的简单技术栈，专注于快速实现核心功能。
"""

import logging
import re
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
from markitdown import MarkItDown

logger = logging.getLogger(__name__)


class PatentLocalizationAgent:
    """专利本地化Agent - 简化版本。
    
    负责将专利网页内容完整本地化并结构化，包括内容转换和图片下载。
    使用MarkItDown进行内容转换，requests进行网页抓取和资源下载。
    """
    
    def __init__(self, timeout: int = 30, max_retries: int = 2):
        """初始化专利本地化Agent。
        
        Args:
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.markitdown = MarkItDown()
        
        # 设置requests会话
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        logger.info("专利本地化Agent初始化完成")
    
    def localize_patent(self, url: str, output_dir: Path) -> Dict[str, Any]:
        """本地化专利网页内容。
        
        Args:
            url: 专利网页URL
            output_dir: 输出目录
            
        Returns:
            本地化结果字典
        """
        logger.info(f"开始本地化专利: {url}")
        
        # 提取专利编号
        patent_id = self._extract_patent_id(url)
        
        try:
            # 创建专利文件夹
            patent_folder = output_dir / patent_id
            patent_folder.mkdir(parents=True, exist_ok=True)
            resource_folder = patent_folder / "resource"
            resource_folder.mkdir(exist_ok=True)
            
            # 初始化进度文件
            progress_file = patent_folder / "progress.md"
            self._init_progress_file(progress_file, url)
            
            # 步骤1: 抓取网页内容
            logger.info("步骤1: 抓取网页内容")
            html_content = self._fetch_webpage(url)
            
            # 保存原始HTML
            raw_html_file = patent_folder / "raw.html"
            raw_html_file.write_text(html_content, encoding='utf-8')
            
            self._update_progress(progress_file, "访问网站并抓取内容", True)
            
            # 步骤2: 下载资源文件
            logger.info("步骤2: 下载资源文件")
            image_urls = self._extract_image_urls(html_content)
            downloaded_resources = self._download_resources(image_urls, resource_folder, progress_file)
            
            # 步骤3: 结构化内容转换
            logger.info("步骤3: 结构化内容转换")
            markdown_content = self._convert_to_structured_markdown(html_content, downloaded_resources)
            
            # 保存结构化Markdown
            patent_md_file = patent_folder / "patent.md"
            patent_md_file.write_text(markdown_content, encoding='utf-8')
            
            self._update_progress(progress_file, "结构化转换为markdown", True)
            
            logger.info(f"专利本地化完成: {patent_folder}")
            
            return {
                "patent_id": patent_id,
                "patent_folder": str(patent_folder),
                "files_created": [
                    "progress.md",
                    "raw.html",
                    "patent.md"
                ],
                "resources_downloaded": len(downloaded_resources),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"专利本地化失败: {e}")
            return {
                "patent_id": patent_id,
                "error": str(e),
                "status": "failed"
            }
    
    def _extract_patent_id(self, url: str) -> str:
        """从URL中提取专利编号。"""
        # 提取专利编号的模式
        patterns = [
            r'patent/([A-Z]{2}\d+[A-Z]?\d*)',  # Google Patents
            r'patent/(US\d+[A-Z]?\d*)',        # USPTO
            r'patent/(CN\d+[A-Z]?\d*)',        # CNIPA
            r'patent/(EP\d+[A-Z]?\d*)',        # EPO
            r'patent/(JP\d+[A-Z]?\d*)',        # JPO
            r'patent/(WO\d+[A-Z]?\d*)',        # WIPO
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # 如果没有匹配到，使用URL的最后一部分
        return url.split('/')[-1].replace('.html', '').replace('.htm', '')
    
    def _fetch_webpage(self, url: str) -> str:
        """抓取网页内容。"""
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"抓取网页 (尝试 {attempt + 1}/{self.max_retries + 1}): {url}")
                
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                logger.info(f"网页抓取成功: {url}")
                return response.text
                
            except Exception as e:
                logger.warning(f"网页抓取失败 (尝试 {attempt + 1}): {e}")
                if attempt == self.max_retries:
                    raise Exception(f"网页抓取最终失败: {e}")
    
    def _extract_image_urls(self, html_content: str) -> List[str]:
        """从HTML内容中提取图片URL。"""
        image_urls = []
        
        # 提取img标签中的src属性
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
        img_matches = re.findall(img_pattern, html_content, re.IGNORECASE)
        image_urls.extend(img_matches)
        
        # 提取background-image中的URL
        bg_pattern = r'background-image:\s*url\(["\']?([^"\']+)["\']?\)'
        bg_matches = re.findall(bg_pattern, html_content, re.IGNORECASE)
        image_urls.extend(bg_matches)
        
        # 去重并过滤无效URL
        unique_urls = []
        seen = set()
        
        for url in image_urls:
            # 清理URL
            url = url.strip()
            if url and (url.startswith(('http://', 'https://')) or url.startswith('//')) and url not in seen:
                # 处理相对URL
                if url.startswith('//'):
                    url = 'https:' + url
                seen.add(url)
                unique_urls.append(url)
        
        logger.info(f"从HTML中提取到 {len(unique_urls)} 个图片URL")
        return unique_urls
    
    def _download_resources(self, image_urls: List[str], resource_folder: Path, progress_file: Path) -> List[Dict[str, str]]:
        """下载资源文件到本地。"""
        downloaded_resources = []
        
        # 更新进度文件，记录资源下载任务
        self._update_progress(progress_file, "下载资源文件", False, resource_urls=image_urls)
        
        for i, image_url in enumerate(image_urls):
            try:
                # 生成本地文件名
                parsed_url = urlparse(image_url)
                file_extension = Path(parsed_url.path).suffix
                if not file_extension:
                    file_extension = '.jpg'  # 默认扩展名
                
                local_filename = f"resource_{i+1:03d}{file_extension}"
                local_path = resource_folder / local_filename
                
                self._update_progress(progress_file, f"正在下载{image_url}", False, current_resource_url=image_url)
                
                # 下载资源
                success = self._download_single_resource(image_url, local_path)
                
                if success:
                    downloaded_resources.append({
                        "url": image_url,
                        "local_path": str(Path("resource") / local_filename),
                        "file_type": file_extension
                    })
                    self._update_progress(progress_file, f"下载资源", True, current_resource_url=image_url)
                    logger.info(f"成功下载资源: {image_url} -> {local_path}")
                else:
                    self._update_progress(progress_file, f"下载资源失败: {image_url}", False, current_resource_url=image_url, failed=True)
                    logger.warning(f"资源下载失败: {image_url}")
                
            except Exception as e:
                logger.warning(f"资源下载异常: {image_url}, 错误: {e}")
                self._update_progress(progress_file, f"资源下载异常: {image_url}, 错误: {e}", False, current_resource_url=image_url, failed=True)
        
        return downloaded_resources
    
    def _download_single_resource(self, url: str, local_path: Path) -> bool:
        """下载单个资源文件。"""
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"下载资源 (尝试 {attempt + 1}/{self.max_retries + 1}): {url}")
                
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                # 确保目录存在
                local_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 写入文件
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"资源下载成功: {url}")
                return True
                
            except Exception as e:
                logger.warning(f"资源下载失败 (尝试 {attempt + 1}): {e}")
                if attempt == self.max_retries:
                    return False
    
    def _convert_to_structured_markdown(self, html_content: str, resources: List[Dict[str, str]]) -> str:
        """将HTML内容转换为结构化的Markdown格式。"""
        try:
            # 使用MarkItDown进行转换
            result = self.markitdown.convert(html_content)
            markdown_content = result.text_content
            
            # 替换图片链接为本地路径
            for resource in resources:
                original_url = resource["url"]
                local_path = resource["local_path"]
                markdown_content = markdown_content.replace(original_url, local_path)
            
            # 添加基础的结构化信息
            structured_content = self._add_patent_structure(markdown_content)
            
            return structured_content
            
        except Exception as e:
            logger.error(f"Markdown转换失败: {e}")
            # 如果转换失败，返回基础的HTML到Markdown转换
            return self._create_fallback_markdown(html_content, resources)
    
    def _add_patent_structure(self, markdown_content: str) -> str:
        """为Markdown内容添加专利结构。"""
        # 简单的结构化处理
        lines = markdown_content.split('\n')
        structured_lines = []
        
        # 添加标题
        structured_lines.append("# 专利文档")
        structured_lines.append("")
        
        # 查找并提取关键信息
        title_found = False
        abstract_found = False
        
        for line in lines:
            # 查找标题
            if not title_found and ('title' in line.lower() or '专利' in line):
                structured_lines.append("## 专利标题")
                structured_lines.append(line.strip())
                structured_lines.append("")
                title_found = True
                continue
            
            # 查找摘要
            if not abstract_found and ('abstract' in line.lower() or '摘要' in line):
                structured_lines.append("## 专利摘要")
                structured_lines.append(line.strip())
                structured_lines.append("")
                abstract_found = True
                continue
            
            # 添加其他内容
            structured_lines.append(line)
        
        return '\n'.join(structured_lines)
    
    def _create_fallback_markdown(self, html_content: str, resources: List[Dict[str, str]]) -> str:
        """创建备用的Markdown格式。"""
        logger.warning("使用备用Markdown格式")
        
        # 简单的HTML标签转换
        content = html_content
        
        # 替换图片链接
        for resource in resources:
            original_url = resource["url"]
            local_path = resource["local_path"]
            content = content.replace(original_url, local_path)
        
        # 简单的HTML标签转换
        content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', content, flags=re.IGNORECASE)
        content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', content, flags=re.IGNORECASE)
        content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', content, flags=re.IGNORECASE)
        content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', content, flags=re.IGNORECASE)
        content = re.sub(r'<br[^>]*>', r'\n', content, flags=re.IGNORECASE)
        
        # 移除其他HTML标签
        content = re.sub(r'<[^>]+>', '', content)
        
        # 构建基础结构
        markdown = f"""# 专利文档

## 原始内容

{content}

## 资源文件

"""
        
        if resources:
            for resource in resources:
                local_path = resource["local_path"]
                markdown += f"- [{Path(local_path).name}]({local_path})\n"
        else:
            markdown += "无资源文件\n"
        
        return markdown
    
    def _init_progress_file(self, progress_file: Path, url: str) -> None:
        """初始化进度文件。"""
        content = f"""## 任务进度
- [ ] 访问网站并抓取内容
- [ ] 下载资源文件  
- [ ] 结构化转换为markdown

## 资源下载进度

## 当前任务
开始处理: {url}
"""
        progress_file.write_text(content, encoding='utf-8')
    
    def _update_progress(
        self, 
        progress_file: Path, 
        task: str, 
        completed: bool, 
        resource_urls: Optional[List[str]] = None,
        current_resource_url: Optional[str] = None,
        failed: bool = False
    ) -> None:
        """更新任务进度。"""
        try:
            content = progress_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # 更新主任务进度
            for i, line in enumerate(lines):
                if task.split(':')[0] in line and line.startswith('- ['):
                    if completed:
                        lines[i] = line.replace('[ ]', '[x]')
                    break
            
            # 更新资源下载进度
            if resource_urls is not None:
                resource_progress_start_idx = -1
                for i, line in enumerate(lines):
                    if "## 资源下载进度" in line:
                        resource_progress_start_idx = i
                        break
                
                if resource_progress_start_idx != -1:
                    # 清空旧的资源进度
                    new_lines = lines[:resource_progress_start_idx + 1]
                    
                    for url in resource_urls:
                        status_char = '[ ]'
                        if current_resource_url == url:
                            if completed:
                                status_char = '[x]'
                            elif failed:
                                status_char = '[x] ❌'  # 标记失败
                            else:
                                status_char = '[ ] ➡️'  # 正在下载
                        new_lines.append(f"{status_char} {url}")
                    lines = new_lines + lines[resource_progress_start_idx + 1 + len(resource_urls):]  # 重新拼接
            
            # 更新当前任务
            current_task_start_idx = -1
            for i, line in enumerate(lines):
                if "## 当前任务" in line:
                    current_task_start_idx = i
                    break
            
            if current_task_start_idx != -1:
                if current_resource_url:
                    if completed:
                        lines[current_task_start_idx + 1] = f"已完成下载: {current_resource_url}"
                    elif failed:
                        lines[current_task_start_idx + 1] = f"下载失败: {current_resource_url}"
                    else:
                        lines[current_task_start_idx + 1] = f"正在下载: {current_resource_url}"
                else:
                    lines[current_task_start_idx + 1] = task
            
            content = '\n'.join(lines)
            progress_file.write_text(content, encoding='utf-8')
            
        except Exception as e:
            logger.warning(f"更新进度文件失败: {e}")

