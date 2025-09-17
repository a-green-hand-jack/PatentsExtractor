
import os
import sys
import time
import logging
import argparse
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
# from concurrent.futures import ProcessPoolExecutor, as_completed  # 暂时禁用多进程
from dotenv import load_dotenv

# 将项目根目录下的 src 目录添加到 Python 解释器的搜索路径中
# 这使得脚本可以直接导入 src/patents_extractor 中的模块
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# 强制 Marker 使用 CPU，以避免在 macOS 上进行多进程处理时出现 MPS 相关错误
os.environ["TORCH_DEVICE"] = "cpu"

load_dotenv()

try:
    import marker
    from marker.models import create_model_dict
    from marker.output import save_output
    from marker.config.parser import ConfigParser
except ImportError:
    print("错误：无法导入 marker 库。请确保已通过 'pip install marker-pdf' 安装。")
    sys.exit(1)


def setup_logging(log_file: Path) -> None:
    """
    配置日志系统，支持同时输出到控制台和文件。

    Args:
        log_file (Path): 日志文件的输出路径。
    """
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def convert_single_pdf(
    pdf_path: Path,
    output_dir: Path,
    models: Dict[str, Any],
    use_llm: bool = False,
    force_ocr: bool = False,
) -> Tuple[str, Optional[str]]:
    """
    使用预加载的模型转换单个 PDF 文件。

    Args:
        pdf_path (Path): 待处理的 PDF 文件路径。
        output_dir (Path): 输出目录路径。
        models (Dict[str, Any]): 预加载的 marker 模型字典。
        use_llm (bool): 是否启用 LLM 增强功能。
        force_ocr (bool): 是否强制执行 OCR。

    Returns:
        Tuple[str, Optional[str]]: 返回一个元组，包含处理结果（成功/失败）和错误信息（如果有）。
    """
    try:
        logging.info(f"正在处理: {pdf_path.name}")
        
        # 动态构建配置
        config_kwargs = {"output_format": "markdown"}
        if use_llm:
            if "GOOGLE_API_KEY" not in os.environ:
                raise ValueError("错误：--use_llm 已启用，但未设置 GOOGLE_API_KEY 环境变量。")
            config_kwargs["use_llm"] = True
        
        if force_ocr:
            config_kwargs["force_ocr"] = True
            
        config_parser = ConfigParser(config_kwargs)
        
        # 获取转换器实例
        converter_cls = config_parser.get_converter_cls()
        converter = converter_cls(
            config=config_parser.generate_config_dict(),
            artifact_dict=models,
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer(),
            llm_service=config_parser.get_llm_service(),
        )

        # 执行转换
        rendered_output = converter(str(pdf_path))
        
        # 保存输出
        save_output(rendered_output, str(output_dir), pdf_path.stem)
        
        logging.info(f"成功转换: {pdf_path.name}")
        return "success", None
    except Exception as e:
        logging.error(f"处理 {pdf_path.name} 时发生错误: {e}", exc_info=True)
        return "failure", str(e)


def main() -> None:
    """
    脚本主入口函数，负责解析参数、调度任务和报告结果。
    """
    parser = argparse.ArgumentParser(
        description="使用 Marker 批量处理 PDF 文件，并将其转换为 Markdown 格式。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("input_dir", type=str, help="包含待处理 PDF 文件的输入文件夹路径。")
    parser.add_argument("output_dir", type=str, help="用于存放转换后的 Markdown 文件的输出文件夹路径。")
    parser.add_argument(
        "--workers",
        type=int,
        default=2,
        help="并行处理的工作进程数 (默认为 2)。"
    )
    parser.add_argument(
        "--use_llm",
        action="store_true",
        help="启用 LLM 增强功能以提高解析精度 (默认关闭)。\n需要设置 GOOGLE_API_KEY 环境变量。"
    )
    parser.add_argument(
        "--force_ocr",
        action="store_true",
        help="对所有文档启用强制 OCR (默认关闭)。"
    )
    parser.add_argument(
        "--max_files",
        type=int,
        default=None,
        help="要转换的最大文件数 (默认处理全部文件)。"
    )
    parser.add_argument(
        "--log_file",
        type=str,
        default=None,
        help="指定日志文件的输出路径 (默认为: <output_dir>/processing.log)。"
    )
    args = parser.parse_args()

    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)
    
    # 确保输出目录存在
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 设置日志
    log_file_path = Path(args.log_file) if args.log_file else output_path / "processing.log"
    setup_logging(log_file_path)

    # 扫描输入目录获取 PDF 文件
    pdf_files = sorted(list(input_path.glob("*.pdf")))
    if not pdf_files:
        logging.warning(f"在 '{input_path}' 中未找到任何 PDF 文件。")
        return

    # 过滤掉已经处理过的文件
    files_to_process = []
    for pdf_file in pdf_files:
        if (output_path / f"{pdf_file.stem}.md").exists():
            logging.info(f"跳过已存在的文件: {pdf_file.name}")
        else:
            files_to_process.append(pdf_file)

    if not files_to_process:
        logging.info("所有 PDF 文件均已处理过，没有新文件需要转换。")
        return
        
    # 应用 max_files 限制
    if args.max_files is not None:
        files_to_process = files_to_process[:args.max_files]
        logging.info(f"根据 --max_files 参数，将处理 {len(files_to_process)} 个文件。")

    # 在主进程中预加载模型
    logging.info("正在加载 Marker 模型 (这可能需要一些时间，请耐心等待)...")
    start_model_load = time.time()
    try:
        loaded_models = create_model_dict()
        logging.info(f"模型加载完毕，耗时 {time.time() - start_model_load:.2f} 秒。")
    except Exception as e:
        logging.critical(f"模型加载失败: {e}", exc_info=True)
        logging.critical("请检查您的 PyTorch 或 marker 安装是否正确。")
        return

    start_time = time.time()
    success_count = 0
    failure_count = 0

    if args.workers > 1:
        logging.warning("由于 macOS 上的 PyTorch 多进程兼容性问题，强制使用单进程模式。")
    
    logging.info(f"开始顺序处理 {len(files_to_process)} 个 PDF 文件...")

    for pdf_path in files_to_process:
        try:
            result, error_msg = convert_single_pdf(
                pdf_path,
                output_path,
                loaded_models,
                args.use_llm,
                args.force_ocr
            )
            if result == "success":
                success_count += 1
            else:
                failure_count += 1
        except Exception as exc:
            logging.error(f"处理 {pdf_path.name} 时产生了一个未捕获的异常: {exc}", exc_info=True)
            failure_count += 1

    end_time = time.time()
    total_time = end_time - start_time

    logging.info("==================== 处理完成 ====================")
    logging.info(f"总耗时: {total_time:.2f} 秒")
    logging.info(f"成功处理文件数: {success_count}")
    logging.info(f"失败处理文件数: {failure_count}")
    logging.info(f"输出文件位于: {output_path.resolve()}")
    logging.info(f"详细日志位于: {log_file_path.resolve()}")
    logging.info("==================================================")


if __name__ == "__main__":
    main()
