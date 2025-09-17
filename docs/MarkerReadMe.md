
# Marker 中文文档

[![PyPI version](https://badge.fury.io/py/marker-pdf.svg)](https://badge.fury.io/py/marker-pdf)
[![Downloads](https://static.pepy.tech/badge/marker-pdf)](https://pepy.tech/project/marker-pdf)

**快速且高精度地将 PDF 转换为 Markdown + JSON。**

[English](/README.md) | [中文](docs/MarkerReadMe.md)

## 特性

*   **速度快**: 批量处理速度极快 (在单个 A100 上可达 ~120 页/秒)。
*   **精度高**: 在移除页眉、页脚、目录和其他噪音方面，比 `nougat` 更出色。在从 PDF 中提取文本和表格方面，优于 `PyPDF`、`unstructured` 和 `llamaparse`。
*   **LLM 友好**: 输出的 Markdown 格式简洁，非常适合与 LLM (大型语言模型) 一起使用。
*   **支持多种语言**: 轻松支持数百种语言。
*   **表格提取**: 能够将表格转换为 Markdown 格式。
*   **数学公式**: 能够将 LaTeX 公式转换为 Mathpix Markdown 格式。
*   **代码块**: 能够正确识别并格式化代码块。
*   **元数据**: 能够提取 PDF 书签和元数据。
*   **容错性**: 能处理损坏的 PDF、OCR 文本和嵌入的图像。

## 安装

1.  **PyTorch 安装**
    Marker 需要 PyTorch。请根据您的系统按照 [官方 PyTorch 安装说明](https://pytorch.org/get-started/locally/) 进行安装。

    对于带有 CUDA 的 Linux/Windows 系统:
    ```bash
    pip install torch
    ```
    对于 Mac:
    ```bash
    pip install torch
    ```

2.  **Marker 安装**
    ```bash
    pip install marker-pdf
    ```

## 使用方法

### 命令行工具 (CLI)

要将单个 PDF 文件转换为 Markdown:
```bash
marker_single "path/to/your/document.pdf" "path/to/your/output.md"
```

要批量转换文件夹中的所有 PDF:
```bash
marker "path/to/your/pdf_folder" "path/to/your/output_folder"
```

*   `--workers`: 并行处理的工作进程数 (默认为 1)。
*   `--max`: 要转换的最大文件数。
*   `--metadata_file`: 将元数据保存到指定的 JSON 文件。
*   `--batch_multiplier`: 每个 GPU 上的批量大小乘数 (默认为 1)。如果遇到内存不足错误，请减小此值。

### Python 库

```python
import marker

# 将单个 PDF 转换为 markdown
# 这将返回文本和一个包含 PDF 书签的元数据字典
text, meta = marker.convert_pdf("document.pdf")

# `meta` 字典将包含书签 (如果有)
# {'toc': [{'title': 'Chapter 1', 'page': 1, 'children': []}]}
```

## 服务器

您可以使用 `convert.py` 脚本启动一个 API 服务器:
```bash
python convert.py
```
这将在 `http://localhost:8001/marker` 启动一个端点。
您可以通过 `chunk_convert.py` 中的 `get_endpoint_options` 查看所有可用的端点选项。

您可以像这样发送请求:
```python
import requests
import json

post_data = {
    'filepath': '文件路径',
    # 在此添加其他参数
}

requests.post("http://localhost:8001/marker", data=json.dumps(post_data)).json()
```
请注意，这不是一个非常健壮的 API，仅适用于小规模使用。

## 故障排查

如果遇到问题，以下设置可能会对您有所帮助:

*   **精度问题**: 尝试设置 `--use_llm` 来使用 LLM 提高质量。您必须将 `GOOGLE_API_KEY` 设置为 Gemini API 密钥才能使用此功能。
*   **文本乱码**: 确保设置 `force_ocr`，这将对文档进行重新 OCR。
*   **`TORCH_DEVICE`**: 设置此环境变量以强制 Marker 使用指定的 Torch 设备进行推理。
*   **内存不足**: 减少工作进程数 (`workers`)。您也可以尝试将长 PDF 拆分成多个文件。

## 调试

传递 `debug` 选项以激活调试模式。这将保存每页带有检测到的布局和文本的图像，并输出一个包含额外边界框信息的 JSON 文件。

## 基准测试

### 整体 PDF 转换

我们通过从 Common Crawl 数据集中提取单个 PDF 页面创建了一个基准测试集。我们使用一种将文本与真实文本段对齐的启发式方法和 LLM 作为评判者进行评分。

| 方法 | 平均时间 | 启发式得分 | LLM 得分 |
|---|---|---|---|
| marker | 2.83837 | 95.6709 | 4.23916 |
| llamaparse | 23.348 | 84.2442 | 3.97619 |
| mathpix | 6.36223 | 86.4281 | 4.15626 |
| docling | 3.69949 | 86.7073 | 3.70429 |

基准测试在 H100 GPU 上运行 marker 和 docling，llamaparse 和 mathpix 使用其云服务。

### 表格转换

Marker 可以使用 `marker.converters.table.TableConverter` 从 PDF 中提取表格。表格提取性能通过比较提取的 HTML 表格表示与 FinTabNet 测试集中的原始 HTML 表示来衡量。

| 方法 | 平均得分 | 总表格数 |
|---|---|---|
| marker | 0.816 | 99 |
| marker w/use_llm | 0.907 | 99 |
| gemini | 0.829 | 99 |

`--use_llm` 标志可以显著提高表格识别性能。

### 如何运行您自己的基准测试

您可以按照说明在您自己的机器上对 Marker 进行基准测试。

## 工作原理

Marker 是一个深度学习模型流水线:
1.  提取文本，必要时进行 OCR (使用启发式方法和 surya)
2.  检测页面布局并找到阅读顺序 (surya)
3.  清理和格式化每个块 (使用启发式方法、texify 和 surya)
4.  (可选) 使用 LLM 提高质量
5.  合并块并对完整文本进行后处理

它只在必要时使用模型，从而提高了速度和准确性。

## 局限性

PDF 是一种棘手的格式，因此 Marker 不会总是完美工作。以下是一些已知的局限性，我们计划在未来解决:

*   非常复杂的布局，如嵌套的表格和表单，可能无法正常工作。
*   表单可能无法很好地呈现。

注意: 使用 `--use_llm` 和 `--force_ocr` 标志将在很大程度上解决这些问题。

## 关于

快速且高精度地将 PDF 转换为 Markdown + JSON。
[www.datalab.to](https://www.datalab.to)
