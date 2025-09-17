import sys,
import logging
from pathlib import Path

# 将项目根目录下的 src 目录添加到 Python 解释器的搜索路径中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# --- 导入 Marker 库的内部组件 ---
from marker.models import create_model_dict
from marker.output import save_output
from marker.config.parser import ConfigParser

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)


def process_pdf(pdf_path: Path, output_dir: Path) -> None:
    """
    使用 Marker 引擎处理单个 PDF 文件，并将结果保存到指定目录。
    此函数基于 marker-pdf==1.9.3 的内部 API 实现。

    Args:
        pdf_path (Path): 输入的 PDF 文件路径。
        output_dir (Path): 输出目录的路径。
    """
    if not pdf_path.is_file():
        logging.error(f"PDF 文件不存在: {pdf_path}")
        return

    logging.info("正在加载 Marker 模型 (这可能需要一些时间)...")
    models = create_model_dict()
    logging.info("模型加载完毕。")

    # 使用默认配置
    # 注意：我们在这里传入一个空的 kwargs 字典，
    # ConfigParser 会使用它的默认值。
    config_parser = ConfigParser({"output_format": "markdown"})

    # 从配置解析器获取转换器类和其实例化所需的组件
    converter_cls = config_parser.get_converter_cls()
    converter = converter_cls(
        config=config_parser.generate_config_dict(),
        artifact_dict=models,
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
        llm_service=config_parser.get_llm_service(),
    )
    
    logging.info(f"开始处理 PDF 文件: {pdf_path.name}")
    try:
        # 调用转换器实例来处理文件
        rendered_output = converter(str(pdf_path))
        
        # 使用 save_output 函数保存结果
        # 它会自动处理文件夹创建和文件写入
        save_output(rendered_output, str(output_dir), pdf_path.stem)

    except Exception as e:
        logging.error(f"处理 PDF 时发生错误: {e}", exc_info=True)
        return

    logging.info(f"所有操作完成。输出位于: {output_dir}/{pdf_path.stem}")


if __name__ == "__main__":
    # 定义项目根目录
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

    # 定义输入和输出路径
    PDF_FILE = PROJECT_ROOT / "data" / "pdf" / "CN202210107337.pdf"
    OUTPUT_BASE_DIR = PROJECT_ROOT / "output"
    
    process_pdf(PDF_FILE, OUTPUT_BASE_DIR)
