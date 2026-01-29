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

`Zotero Unleashed` 不仅仅是一个导出工具，它是你本地知识库的解放者。它打破 Zotero 数据库的黑盒限制，将你的科研文献以 **1:1 完美镜像** 的形式映射到本地硬盘，构建一个**清晰、有序、自由**的文件帝国。

---

## 🚀 Why Zotero Unleashed?

你的文献不应被禁锢在晦涩的数据库 ID 中。

- **🔮 Mirror Protocol (全息镜像)**: 
  完美复刻 Zotero 的 Collection 层级结构。你在 Zotero 里怎么整理，硬盘上就怎么呈现。
  
- **🧠 Intelligent Sort (智能分流)**: 
  自动识别文件元数据，将 `PDF`、`Word` 和其他格式自动归类。告别杂乱无章。
  
- **🏷️ Semantic Naming (语义化命名)**: 
  拒绝 `ab12cd.pdf` 这样的乱码。文件自动重命名为 `[年份] 作者 - 标题.ext`，一眼识别核心信息。

- **🛡️ Zero-Touch Safety (零触碰安全)**: 
  采用只读模式连接 `zotero.sqlite`。你的原始数据神圣不可侵犯，我们只做最安全的搬运工。

## 🛠️ Quick Start

无需繁琐配置，**Python 原生驱动**，即刻运行。

### 环境要求
- Python 3.8+
- 安装依赖库: `pip install -r requirements.txt` (仅需轻量级 Web 框架支持)

### 极速运行 (Web UI)

推荐使用全新的可视化界面，操作更直观。

1. **Windows 用户**: 直接双击项目根目录下的 **`start.bat`**。
2. **终端启动**:
   ```bash
   python main.py --web
   ```
   *或者在 `.env` 中设置 `CONFIG_SOURCE=web` 后直接运行 `python main.py`*

3. 浏览器会自动打开 **http://127.0.0.1:8000**。
4. 在左侧选择目标 **Collection**，勾选需要导出的子文件夹。
5. 点击 **Start Export**，静待完成。

### 命令行模式 (Backend Only)

如果你需要编写自动化脚本或进行全量导出（确保 `.env` 中 `CONFIG_SOURCE=backend`）：

```bash
python main.py "Your Collection Name"
```

## ⚙️ Configuration

项目开箱即用，但你也通过 `.env` 文件进行微调：

- `ZOTERO_DATA_DIR`: Zotero 数据目录路径 (包含 `zotero.sqlite`)。
- `EXPORT_OUTPUT_ROOT`: 导出文件的存放根目录。
- `DEFAULT_COLLECTION`: 默认选中的 Collection 名称。

## 📂 Project Structure

- `web/`: 前端源码 (HTML/CSS/JS, 零编译构建)
- `src/`: 核心后端逻辑 (Exporter, Database Connector)
- `main.py`: 统一程序入口 (CLI & Web Server)
- `start.bat`: Windows 一键启动脚本

