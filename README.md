# ⚡ Zotero Unleashed
> **Set your files free.** | 释放你的文献，重塑知识秩序。

<div align="center">

![GitHub Release](https://img.shields.io/github/v/release/Jin-sjh/Zotero-Unleashed?style=flat-square&color=blueviolet)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/Jin-sjh/Zotero-Unleashed/total?style=flat-square&color=success)
![GitHub Repo stars](https://img.shields.io/github/stars/Jin-sjh/Zotero-Unleashed?style=flat-square&logo=github)
![GitHub issues](https://img.shields.io/github/issues/Jin-sjh/Zotero-Unleashed?style=flat-square&color=orange)
![GitHub license](https://img.shields.io/github/license/Jin-sjh/Zotero-Unleashed?style=flat-square)

</div>

<img width="650" height="280" alt="Image" src="https://github.com/user-attachments/assets/3a037f19-e444-4fb1-9432-2270bc480d7f" />

`Zotero Unleashed` 不仅仅是一个导出工具，它是你本地知识库的解放者与智能管家。它打破 Zotero 数据库的黑盒限制，将你的科研文献以 **1:1 完美镜像** 的形式映射到本地硬盘，并通过 **AI 驱动** 的智能分析，构建一个**清晰、有序、智能**的文献帝国。

---

## 🚀 Why Zotero Unleashed?

你的文献不应被禁锢在晦涩的数据库 ID 中，更应该被智能化管理。

### 核心功能

- **🔮 Mirror Protocol (全息镜像)**: 
  完美复刻 Zotero 的 Collection 层级结构。你在 Zotero 里怎么整理，硬盘上就怎么呈现。
  
- **🧠 Intelligent Sort (智能分流)**: 
  自动识别文件元数据，将 `PDF`、`Word` 和其他格式自动归类。告别杂乱无章。
  
- **🏷️ Semantic Naming (语义化命名)**: 
  拒绝 `ab12cd.pdf` 这样的乱码。文件自动重命名为 `[年份] 作者 - 标题.ext`，一眼识别核心信息。

- **🛡️ Zero-Touch Safety (零触碰安全)**: 
  采用只读模式连接 `zotero.sqlite`。你的原始数据神圣不可侵犯，我们只做最安全的搬运工。

### AI 智能增强 🤖

- **🏷️ Auto-Tagging (智能标签)**: 
  基于 NLP 技术自动分析文献内容，生成精准的主题标签，让文献分类更智能。

- **🔬 Field Classification (领域分类)**: 
  自动识别文献所属研究领域，帮助你快速构建学科知识图谱。

- **🔍 Duplicate Detection (查重去重)**: 
  利用相似度算法智能检测重复文献，避免冗余存储，保持库的整洁。

- **📊 Content Clustering (内容聚类)**: 
  基于内容相似度自动聚类文献，发现隐藏的知识关联，构建主题网络。

- **📝 Enhanced Summarization (智能摘要)**: 
  集成大语言模型（支持 OpenAI 兼容 API），自动生成文献摘要和深度分析。

## 🛠️ Quick Start

无需繁琐配置，**Python 原生驱动**，即刻运行。

### 环境要求
- Python 3.8+
- 安装依赖库: `pip install -r requirements.txt`

### 极速运行 (Web UI)

推荐使用全新的可视化界面，操作更直观，支持 AI 功能。

1. **Windows 用户**: 直接双击项目根目录下的 **`start.bat`**。
2. **终端启动**:
   ```bash
   python main.py --web
   ```
   *或者在 `.env` 中设置 `CONFIG_SOURCE=web` 后直接运行 `python main.py`*

3. 浏览器会自动打开 **http://127.0.0.1:8000**。
4. 在左侧选择目标 **Collection**，勾选需要导出的子文件夹。
5. 点击 **Start Export**，静待完成。
6. 使用 AI 功能对文献进行智能分析和组织。

### 命令行模式 (Backend Only)

如果你需要编写自动化脚本或进行全量导出（确保 `.env` 中 `CONFIG_SOURCE=backend`）：

```bash
python main.py "Your Collection Name"
```

## ⚙️ Configuration

项目开箱即用，但你也可以通过 `.env` 文件进行微调：

### 基础配置
- `ZOTERO_DATA_DIR`: Zotero 数据目录路径 (包含 `zotero.sqlite`)
- `EXPORT_OUTPUT_ROOT`: 导出文件的存放根目录
- `DEFAULT_COLLECTION`: 默认选中的 Collection 名称
- `CONFIG_SOURCE`: 配置来源 (`backend` | `web`)

### AI 功能配置
- `AI_MODEL_TYPE`: AI 模型类型 (`local` | `openai`)
- `LOCAL_AI_MODEL`: 本地模型名称 (默认: `all-MiniLM-L6-v2`)
- `SIMILARITY_THRESHOLD`: 相似度阈值 (默认: `0.8`)
- `MAX_BATCH_SIZE`: 批处理大小 (默认: `100`)
- `OPENAI_API_KEY`: OpenAI API 密钥 (使用 OpenAI 模型时必填)
- `OPENAI_BASE_URL`: OpenAI API 基础 URL (默认: `https://api.openai.com/v1`)
- `AI_ENABLE_CACHE`: 启用 AI 缓存 (默认: `true`)
- `AI_CACHE_TTL`: 缓存过期时间（秒）(默认: `3600`)

## 🤖 AI Features

### 支持的 AI 功能

1. **Auto-Tagging (自动标签)**
   - 基于文献标题、摘要和关键词自动生成主题标签
   - 使用 NLP 技术提取核心概念

2. **Field Classification (领域分类)**
   - 自动识别文献所属研究领域
   - 支持多学科交叉分类

3. **Duplicate Detection (查重检测)**
   - 基于内容相似度检测重复文献
   - 可自定义相似度阈值

4. **Content Clustering (内容聚类)**
   - 自动将相似文献聚类分组
   - 支持 K-means、DBSCAN 等算法

5. **Enhanced Summarization (智能摘要)**
   - 集成大语言模型生成文献摘要
   - 支持 OpenAI 兼容 API

### API 端点

所有 AI 功能通过 Web UI 或 REST API 访问：

- `POST /api/ai/auto-tag` - 自动标签
- `POST /api/ai/classify-field` - 领域分类
- `POST /api/ai/duplicate-detection` - 查重检测
- `POST /api/ai/content-cluster` - 内容聚类
- `POST /api/ai/enhanced-summarize` - 智能摘要
- `POST /api/ai/process-batch` - 批量处理

## 📂 Project Structure

```
Zotero-Unleashed/
├── web/                    # 前端源码 (HTML/CSS/JS, 零编译构建)
│   ├── index.html         # 主界面
│   ├── app.js             # 前端逻辑
│   └── style.css          # 样式文件
├── src/                    # 核心后端逻辑
│   ├── core/              # 核心模块
│   │   ├── config.py      # 配置管理
│   │   └── db_connector.py # 数据库连接器
│   ├── features/          # 功能模块
│   │   └── exporter.py    # 镜像导出器
│   ├── ai/                # AI 功能模块
│   │   ├── ai_processor.py      # AI 处理器
│   │   ├── nlp_utils.py         # NLP 工具
│   │   ├── similarity_engine.py # 相似度引擎
│   │   ├── clustering_engine.py # 聚类引擎
│   │   └── llm_client.py        # LLM 客户端
│   ├── web/               # Web 服务器
│   │   └── server.py      # FastAPI 服务器
│   └── utils/             # 工具函数
│       └── utils.py       # 通用工具
├── main.py                # 统一程序入口 (CLI & Web Server)
├── start.bat              # Windows 一键启动脚本
├── requirements.txt       # Python 依赖
├── .env.example           # 环境配置示例
└── README.md              # 项目文档
```

## 🔧 技术栈

- **Backend**: Python 3.8+, FastAPI, SQLite
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **AI/ML**: 
  - Transformers (Hugging Face)
  - Sentence-Transformers
  - Scikit-learn
  - PyTorch
  - OpenAI API (可选)
- **Database**: SQLite (只读模式)

## 🌟 特性亮点

- ✅ 零依赖前端，无需 Node.js 或构建工具
- ✅ 纯 Python 实现，跨平台兼容
- ✅ 只读数据库访问，100% 安全
- ✅ 支持本地 AI 模型和云端 API
- ✅ RESTful API 设计，易于集成
- ✅ 可视化 Web 界面，操作直观
- ✅ 命令行模式，支持自动化脚本

## 📝 使用场景

1. **文献备份**: 将 Zotero 文献库完整镜像到本地硬盘
2. **知识管理**: 通过 AI 自动分类和标签化文献
3. **查重去重**: 智能检测并清理重复文献
4. **主题研究**: 基于内容聚类发现研究主题
5. **文献综述**: 使用 AI 生成文献摘要和分析

## 🤝 Contributing

欢迎提交 Issue 和 Pull Request！

## 📄 License

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 Acknowledgments

感谢所有为开源社区做出贡献的开发者。

---

<div align="center">

**Made with ❤️ for researchers and knowledge workers**

[⭐ Star this repo](https://github.com/Jin-sjh/Zotero-Unleashed) | [🐛 Report Bug](https://github.com/Jin-sjh/Zotero-Unleashed/issues) | [💡 Request Feature](https://github.com/Jin-sjh/Zotero-Unleashed/issues)

</div>

