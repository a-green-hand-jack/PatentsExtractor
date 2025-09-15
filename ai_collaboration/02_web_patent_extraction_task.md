# 任务：实现专利网页完整本地化Agent

## 1. 🎯 核心目标 (High-Level Goal)

- **用户原始需求**: `实现workflow的第一部分，也就是提取结构化数据。更进一步的，我们先实现第一部分的第一功能，也就是提取网页上的专利信息。`
- **AI 澄清后的目标**: `创建一个专门的专利本地化Agent，使用LLM + 工具调用的方式实现专利网页的完整本地化，包括网页内容获取、图片下载、Markdown转换和文件组织。`
- **验收标准 (Success Criteria)**: 
  - 创建一个PatentLocalizationAgent，能够接收专利URL并完成本地化
  - Agent能够使用lynx工具读取网页内容
  - Agent能够使用curl工具下载图片资源
  - Agent能够将网页内容转换为Markdown格式
  - Agent能够创建结构化的文件夹并保存文件
  - Agent具备完善的错误处理和重试机制
  - Agent提供完整的类型注解和文档字符串

---

## 2. 📝 任务拆解 (Todo List)

- [ ] **步骤 1**: `创建专利本地化Agent类`
  - [ ] 1.1: `创建PatentLocalizationAgent类`
  - [ ] 1.2: `设计Agent的System Prompt`
  - [ ] 1.3: `集成lynx和curl工具调用`

- [ ] **步骤 2**: `实现工具调用接口`
  - [ ] 2.1: `实现lynx网页内容读取工具`
  - [ ] 2.2: `实现curl图片下载工具`
  - [ ] 2.3: `实现文件系统操作工具`

- [ ] **步骤 3**: `设计Agent的System Prompt`
  - [ ] 3.1: `基于gemini-cli的提示词设计本地化流程`
  - [ ] 3.2: `定义文件夹结构和文件命名规则`
  - [ ] 3.3: `设计Markdown转换和图片链接替换逻辑`

- [ ] **步骤 4**: `集成到现有的Agent系统`
  - [ ] 4.1: `将PatentLocalizationAgent集成到StructuredAgentNode`
  - [ ] 4.2: `修改工作流以支持本地化模式`
  - [ ] 4.3: `保持向后兼容性`

- [ ] **步骤 5**: `添加配置和依赖管理`
  - [ ] 5.1: `确保系统有lynx和curl工具`
  - [ ] 5.2: `添加Agent配置选项`
  - [ ] 5.3: `配置输出目录和文件命名规则`

- [ ] **步骤 6**: `编写单元测试`
  - [ ] 6.1: `创建Agent测试用例`
  - [ ] 6.2: `测试各种专利网站的本地化`
  - [ ] 6.3: `测试工具调用和错误处理`

- [ ] **步骤 7**: `完善文档和类型注解`
  - [ ] 7.1: `添加完整的Docstrings`
  - [ ] 7.2: `完善类型注解`
  - [ ] 7.3: `更新模块文档`

---

## 3. ⚙️ 执行日志与进度 (Execution Log & Progress)

### 当前状态：准备开始执行

**分析结果**：
- 现有代码结构良好，已有完整的Agent系统架构
- `src/patents_extractor/agents/` 目录下已有多个Agent节点
- 项目已配置了LangGraph工作流和模型管理
- 需要创建一个专门的专利本地化Agent，而不是手动实现复杂的集成

**技术选型确认**：
- 使用现有的Agent架构，创建PatentLocalizationAgent
- 使用lynx工具进行网页内容读取
- 使用curl工具进行图片下载
- 使用LLM进行内容转换和文件组织
- 集成到现有的StructuredAgentNode中

**下一步行动**：
准备开始执行步骤1，创建PatentLocalizationAgent类并设计System Prompt。

---

## 4. 🔧 技术实现细节

### 4.1 Agent架构设计
```python
class PatentLocalizationAgent:
    """专利本地化Agent"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.llm = self._initialize_llm()
        self.tools = self._initialize_tools()
    
    def localize_patent(self, url: str, output_dir: Path) -> Dict[str, Any]:
        """本地化专利网页内容"""
        pass
    
    def _initialize_tools(self) -> List[Tool]:
        """初始化工具：lynx, curl, file operations"""
        pass
```

### 4.2 System Prompt设计
基于gemini-cli的提示词，设计专利本地化的System Prompt：
- 定义本地化流程：访问网站 → 下载图片 → 改写markdown → 保存文件
- 定义文件夹结构：`patent_folder/patent.md` + `patent_folder/images/`
- 定义图片链接替换逻辑
- 定义错误处理和重试机制

### 4.3 工具集成
- **lynx工具**：用于读取网页内容，获取文本和图片链接
- **curl工具**：用于下载图片资源
- **文件操作工具**：用于创建文件夹和保存文件
- **LLM工具**：用于内容转换和格式化

### 4.4 集成方案
- 创建PatentLocalizationAgent类
- 集成到StructuredAgentNode中作为新的处理模式
- 保持原有的extract_content方法作为备用
- 在workflow中添加本地化选项

---

## 5. 📋 验收检查清单

- [ ] 成功创建PatentLocalizationAgent类
- [ ] Agent能够使用lynx工具读取网页内容
- [ ] Agent能够使用curl工具下载图片资源
- [ ] Agent能够将网页内容转换为Markdown格式
- [ ] Agent能够创建结构化的文件夹：`patent_folder/patent.md` 和 `patent_folder/images/`
- [ ] Markdown文件中的图片链接正确指向本地图片路径
- [ ] Agent具备完善的错误处理和重试机制
- [ ] Agent成功集成到现有的Agent系统中
- [ ] 代码符合项目编码规范
- [ ] 包含完整的类型注解
- [ ] 通过所有单元测试
- [ ] 文档完整且准确

---

## 6. 🚀 后续扩展计划

- 支持更多专利网站（USPTO、EPO、CNIPA等）
- 添加图片OCR处理功能
- 实现增量更新机制
- 添加缓存功能避免重复下载
- 支持批量专利本地化
- 添加进度条和日志记录
- 支持自定义Markdown模板
- 优化Agent的System Prompt以提高准确性
