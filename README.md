# 🚀 智扫通机器人智能管家

本项目是一个基于大语言模型 (LLM) 和 ReAct 架构构建的 **Agent 智能问答管家系统**，专门针对“扫地机器人”及相关业务场景进行知识解答与智能服务。项目集成了 **RAG（检索增强生成）** 以及丰富的 **外部工具调用 (Tools)**，并提供基于 Streamlit 的现代化 Web 交互界面。

## ✨ 功能特性

1. **智能对话交互界面** 💬
   - 提供基于 Streamlit 构建的美观 Chat UI（仿微信聊天气泡UI设计）。
   - 支持流式输出 (Streaming) 和打字机效果，提升用户体验。
   - 实时展示 Agent 思考和工具调用状态（如正在调用工具、正在生成回答）。
   
2. **知识库 Web 管理端** 📂
   - 提供可视化知识库更新服务，支持用户通过 Web 页面上传 `.txt`、`.pdf`、`.docx` 等格式文件。
   - 自动解析上传的文件并将其灌入向量数据库，实现知识库的动态扩容。

3. **强大的 RAG 核心服务** 🧠
   - 内置检索增强生成 (RAG) 链路，将用户问题与本地向量库中的专业文档片段相结合。
   - 支持历史会话记忆功能 (Memory)，能够进行连贯的多轮对话。

4. **ReAct 智能体架构** 🛠️
   - 采用 LangChain 的 ReAct Agent 框架。
   - Agent 具备自主思考与调度能力，集成了多项实用工具：
     - `rag_summary`: 知识库内容检索与总结。
     - `get_weather` / `get_user_location`: 实时天气与用户地理位置获取。
     - `get_current_month` / `fetch_external_data`: 获取当前时间及拉取外部数据。
     - `fill_context_for_report` / `get_user_id`: 报告上下文生成与用户信息读取。
   - 包含自定义中间件拦截器（用于监控工具、记录日志、动态切换Prompt等）。

5. **底层模型生态** 🤖
   - 深度集成阿里云灵积平台 (DashScope)。
   - 语言模型使用 `ChatTongyi` (通义千问)。
   - 向量嵌入使用 `DashScopeEmbeddings`。

## 🏗️ 核心模块结构

项目结构清晰，主要包含以下核心目录：

- **`web/`** - Web 界面层
  - `web_user_question.py`: 面向用户的核心对话界面。
  - `web_file_uploader.py`: 面向管理员的知识库文档上传界面。
- **`agent/`** - 智能体核心逻辑
  - `agent_react.py`: ReAct Agent 的初始化与流式执行逻辑定义。
  - `agent_tools.py`: Agent 所需各种工具函数的具体实现。
  - `agent_middleware.py`: 拦截器及中间件。
- **`rag/`** - 检索增强生成模块
  - `rag_core.py`: RAG 执行链 (Chain) 及对话历史串联。
  - `vector_stores.py`: 向量数据库操作客户端。
  - `file_chat_history_store.py`: 基于文件的聊天记录存储逻辑。
- **`model/`** - 模型工厂
  - `factory.py`: 大模型与 Embedding 模型的实例化与配置。
- **`utils/`** - 工具包
  - 包含配置处理 (`config_handler.py`)、日志 (`logger_handler.py`)、Prompt处理 (`prompt_handler.py`) 等公共方法。

## 🚀 运行说明

### 1. 环境准备
请确保你已经安装了 Python 3.9 或以上版本，并安装依赖包（请根据你的 `requirements.txt` 进行安装）：
```
pip install -r requirements.txt
```

*(注意：你需要配置好阿里云 DashScope 的 API Key 环境变量，例如 `DASHSCOPE_API_KEY`)*

### 2. 启动用户对话界面
在项目根目录下运行以下命令启动 Streamlit 聊天服务：
```
streamlit run web/web_user_question.py
```

### 3. 启动知识库更新界面
如果你需要上传新的文档以更新 RAG 知识库，请在另一个终端窗口运行：
```
streamlit run web/web_file_uploader.py
```

## 📝 待办事项 / 未来规划
- [ ] 接入更多的第三方数据源 API。
- [ ] 优化前端界面的多会话管理能力。
- [ ] 提升解析 `.pdf` 及 `.docx` 复杂表格和图片的能力。
