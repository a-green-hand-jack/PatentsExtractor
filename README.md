# Patents Extractor

一个基于多Agent系统的专利信息智能提取工具，能够从PDF文件或网页链接中提取用户关心的特定内容。

## 功能特性

- **多Agent系统架构**: 结构化Agent、问答Agent、输出Agent协同工作
- **多模态处理**: 同时处理文本和图片内容
- **灵活输入**: 支持PDF文件和专利网页链接
- **智能问答**: 通过多轮对话完善问题描述
- **双格式输出**: 提供Markdown和JSON两种格式，确保内容一致性
- **模板系统**: 支持内置模板和用户自定义模板

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/a-green-hand-jack/PatentsExtractor.git
cd PatentsExtractor

# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
uv pip install -e .
```

### 配置

复制环境变量模板并配置：

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥
```

### 使用示例

```bash
# 从PDF文件提取信息
patents-extractor --input patent.pdf --question "权利要求书中关于蛋白质的氨基酸序列的要求"

# 从网页链接提取信息
patents-extractor --input "https://patents.google.com/patent/US12345678" --question "发明的主要技术特征"

# 使用自定义模板
patents-extractor --input patent.pdf --question "技术方案" --template custom_template.json
```

## 项目结构

```
PatentsExtractor/
├── src/patents_extractor/     # 核心源代码
│   ├── agents/               # Agent实现
│   ├── core/                 # 核心业务逻辑
│   ├── models/               # 数据模型
│   └── utils/                # 工具函数
├── tests/                    # 测试代码
├── scripts/                  # 辅助脚本
├── docs/                     # 项目文档
├── configs/                  # 配置文件
└── output/                   # 输出目录
```

## 技术栈

- **Python 3.9+**: 主要编程语言
- **LangGraph**: 多Agent系统框架
- **Qwen2.5-VL**: 多模态模型
- **Qwen2.5-Max**: 语言模型
- **Chroma**: 向量数据库
- **BeautifulSoup**: 网页解析
- **PyMuPDF**: PDF处理

## 开发

### 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest -m unit

# 运行集成测试
pytest -m integration

# 生成覆盖率报告
pytest --cov=src/patents_extractor --cov-report=html
```

### 代码格式化

```bash
# 格式化代码
black src/ tests/
isort src/ tests/

# 类型检查
mypy src/
```

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License
