# ⚡ Zotero Unleashed
> **Set your files free.** | 释放你的文献，重塑知识秩序。

<div align="center">

![GitHub Release](https://img.shields.io/github/v/release/Jin-sjh/Zotero-Unleashed?style=flat-square&color=blueviolet)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/Jin-sjh/Zotero-Unleashed/total?style=flat-square&color=success)
![GitHub Repo stars](https://img.shields.io/github/stars/Jin-sjh/Zotero-Unleashed?style=flat-square&logo=github)
![GitHub issues](https://img.shields.io/github/issues/Jin-sjh/Zotero-Unleashed?style=flat-square&color=orange)
![GitHub license](https://img.shields.io/github/license/Jin-sjh/Zotero-Unleashed?style=flat-square)

</div>

<img width="1024" height="829" alt="Image" src="https://github.com/user-attachments/assets/3a037f19-e444-4fb1-9432-2270bc480d7f" />

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
- Python 3.x
- **No Dependencies**: 没错，无需 `pip install` 任何第三方库。

### 极速运行

```bash
# 格式: python main.py [分类名称] --out [目标路径]

python main.py "My Thesis" --out "D:\My_Library"
```

> **Pro Tip**: 如果不指定 `--out`，默认将在当前目录创建 `Zotero_Export` 基地。

## 📖 Advanced Usage

```bash
python main.py "Deep Learning" \
    --zotero-data "C:\Users\Admin\Zotero" \
    --out "E:\Research\AI_Papers"
```

| 参数 | 说明 |
| :--- | :--- |
| `collection` | **(必填)** 目标根分类名称。支持模糊匹配。 |
| `--out` | 导出目的地。你的知识将在此重建。 |
| `--zotero-data` | Zotero 数据源路径 (默认自动探测 Windows 默认路径)。 |

---

