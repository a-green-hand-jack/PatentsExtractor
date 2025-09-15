"""专利提取器命令行接口。"""

import logging
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler

from patents_extractor import PatentExtractor
from patents_extractor.models.patent import PatentQuery


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("patents_extractor")
console = Console()


@click.command()
@click.option(
    "--input", "-i",
    required=True,
    help="输入文件路径或网页URL"
)
@click.option(
    "--question", "-q",
    required=True,
    help="用户关心的问题描述"
)
@click.option(
    "--template", "-t",
    help="输出模板文件路径（可选）"
)
@click.option(
    "--output-format", "-f",
    type=click.Choice(["markdown", "json", "both"]),
    default="both",
    help="输出格式"
)
@click.option(
    "--output-dir", "-o",
    type=click.Path(exists=False),
    help="输出目录"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="详细输出"
)
def main(
    input: str,
    question: str,
    template: Optional[str],
    output_format: str,
    output_dir: Optional[str],
    verbose: bool
) -> None:
    """专利信息提取器 - 从专利文档中提取用户关心的信息。
    
    示例:
        patents-extractor -i patent.pdf -q "权利要求书中关于蛋白质的氨基酸序列的要求"
        patents-extractor -i "https://patents.google.com/patent/US12345678" -q "发明的主要技术特征"
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 创建专利查询对象
        query = PatentQuery(
            input_source=input,
            question=question,
            template_path=template,
            output_format=output_format,
            output_dir=Path(output_dir) if output_dir else None
        )
        
        # 初始化提取器
        extractor = PatentExtractor()
        
        # 执行提取
        console.print("[bold blue]开始处理专利文档...[/bold blue]")
        result = extractor.extract(query)
        
        # 输出结果
        if output_format in ["markdown", "both"]:
            console.print("\n[bold green]Markdown格式输出:[/bold green]")
            console.print(result.markdown_output)
        
        if output_format in ["json", "both"]:
            console.print("\n[bold green]JSON格式输出:[/bold green]")
            console.print(result.json_output)
        
        # 保存到文件
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            if output_format in ["markdown", "both"]:
                markdown_file = output_path / "result.md"
                markdown_file.write_text(result.markdown_output, encoding="utf-8")
                console.print(f"[green]Markdown结果已保存到: {markdown_file}[/green]")
            
            if output_format in ["json", "both"]:
                json_file = output_path / "result.json"
                json_file.write_text(result.json_output, encoding="utf-8")
                console.print(f"[green]JSON结果已保存到: {json_file}[/green]")
        
        console.print("[bold green]处理完成![/bold green]")
        
    except Exception as e:
        logger.error(f"处理过程中发生错误: {e}")
        console.print(f"[bold red]错误: {e}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
