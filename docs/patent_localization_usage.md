# 专利网页本地化工具使用说明

## 功能概述

专利网页本地化工具能够将Google Patents等专利网站的网页内容完整地本地化并结构化，包括：

- 网页内容抓取和HTML保存
- 图片资源下载
- 结构化Markdown转换
- 进度跟踪

## 安装依赖

```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
uv pip install "markitdown[all]" requests
```

## 使用方法

### 1. 命令行工具

```bash
# 基本用法
python scripts/patent_localization_cli.py "https://patents.google.com/patent/CN116555216A/en"

# 指定输出目录
python scripts/patent_localization_cli.py "https://patents.google.com/patent/CN116555216A/en" -o ./my_output

# 详细输出
python scripts/patent_localization_cli.py "https://patents.google.com/patent/CN116555216A/en" -v

# 自定义超时和重试次数
python scripts/patent_localization_cli.py "https://patents.google.com/patent/CN116555216A/en" --timeout 60 --max-retries 3
```

### 2. Python API

```python
from pathlib import Path
from patents_extractor import PatentLocalizationAgent

# 创建Agent
agent = PatentLocalizationAgent()

# 本地化专利
url = "https://patents.google.com/patent/CN116555216A/en"
output_dir = Path("output/patents")

result = agent.localize_patent(url, output_dir)
print(f"本地化结果: {result}")
```

## 输出结构

每个专利会生成以下文件结构：

```
{专利编号}/
├── progress.md              # 进度记录
├── raw.html                 # 原始网页内容（HTML格式）
├── patent.md                # 结构化Markdown（保持原语言）
└── resource/                # 资源文件夹
    ├── resource_001.png
    ├── resource_002.pdf
    └── ...
```

## 功能特性

- **网页抓取**: 使用requests进行网页内容抓取
- **内容转换**: 使用MarkItDown进行HTML到Markdown的转换
- **资源下载**: 自动下载图片等资源文件
- **进度跟踪**: 实时更新处理进度
- **错误处理**: 完善的错误处理和重试机制
- **专利编号提取**: 自动从URL中提取专利编号

## 支持的专利网站

- Google Patents
- USPTO
- CNIPA
- EPO
- JPO
- WIPO

## 配置选项

### Agent初始化参数

- `timeout`: 请求超时时间（秒），默认30
- `max_retries`: 最大重试次数，默认2

### CLI参数

- `-o, --output`: 输出目录
- `-v, --verbose`: 详细输出
- `--timeout`: 请求超时时间
- `--max-retries`: 最大重试次数

## 示例输出

### 成功结果

```json
{
  "patent_id": "CN116555216A",
  "patent_folder": "output/patents/CN116555216A",
  "files_created": ["progress.md", "raw.html", "patent.md"],
  "resources_downloaded": 5,
  "status": "success"
}
```

### 失败结果

```json
{
  "patent_id": "CN116555216A",
  "error": "网页抓取失败: Connection timeout",
  "status": "failed"
}
```

## 注意事项

1. 确保网络连接正常
2. 某些专利网站可能有反爬虫机制
3. 大文件下载可能需要较长时间
4. 建议在虚拟环境中使用

## 故障排除

### 常见问题

1. **网页抓取失败**
   - 检查网络连接
   - 增加超时时间
   - 增加重试次数

2. **资源下载失败**
   - 检查资源URL是否有效
   - 某些资源可能需要特殊权限

3. **Markdown转换失败**
   - 系统会自动使用备用格式
   - 检查原始HTML内容是否完整

### 日志查看

使用详细模式查看详细日志：

```bash
python scripts/patent_localization_cli.py "URL" -v
```

## 技术架构

- **网页抓取**: requests + User-Agent伪装
- **内容转换**: MarkItDown库
- **文件管理**: pathlib
- **进度跟踪**: 实时更新progress.md文件
- **错误处理**: 多级重试机制

## 更新日志

- v0.1.0: 初始版本，支持基本的专利网页本地化功能

