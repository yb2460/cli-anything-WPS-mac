# harness-anything-mac

<h3 align="center">跨平台 AI Agent 工具集 —— 办公 + 设计 + 学术 全栈操控</h3>

<p align="center">
  <img src="https://img.shields.io/badge/平台-Windows%20%7C%20macOS%20%7C%20Linux-blue" alt="Platform">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/协议-MIT-green" alt="License">
</p>

---

## 包含项目

### 1. cli-anything-office — 跨平台 Office 操控

- **Windows**：WPS COM 或 Microsoft Office COM（PowerPoint/Word/Excel）
- **macOS/Linux**：LibreOffice headless

```bash
cli-anything-office document new --type writer --name "报告"
cli-anything-office export render report.pdf -p pdf
cli-anything-office preset apply academic --talk-type conference
```

PPT 设计系统：4 套预设 + 14 种布局 + 5 维度质量审查

---

### 2. cli-anything-zotero — 学术研究智能体

文献管理 + 27 个学术 Skill 集成。写综述、写论文、审稿、做图表一站式。

```bash
cli-anything-zotero skills list                    # 列出所有学术 Skill
cli-anything-zotero skills pipeline thesis          # 学位论文推荐流程
cli-anything-zotero skills journal "Nature"         # 期刊图表规范
```

**7 大 Skill 分类**：search(3) / research(4) / writing(5) / review(5) / visualization(4) / analysis(3) / pipeline(2)

---

### 3. Illustrator Harness — Adobe Illustrator AI Agent

通过 COM 自动化（Windows）或 AppleScript/JXA（macOS）操控 **Adobe Illustrator**，让 AI Agent 直接创建和编辑矢量图形。

```bash
cd illustrator-harness/agent-harness
pip install -e .
```

| 命令组 | 功能 |
|--------|------|
| `project` | 新建/打开/保存 AI 文档 |
| `layers` | 图层增删改、可见性、锁定 |
| `shapes` | 矩形、椭圆、线条、多边形绘制 |
| `text` | 文字添加/修改（字体、大小、颜色） |
| `export` | 导出 PNG / JPEG / SVG / PDF / AI |

```bash
cli-anything-illustrator project new logo.ai -w 500 -h 500
cli-anything-illustrator text add "Brand" --x 100 --y 100 --font "Arial" --size 72
cli-anything-illustrator shapes rect --x 50 --y 50 --w 200 --h 100
cli-anything-illustrator export svg output.svg
```

**前置条件**：Python 3.10+ + click；Windows 需 pywin32 + Illustrator 2023+；macOS 需 Illustrator 2023+

---

### 4. Photoshop Harness — Adobe Photoshop AI Agent

通过 COM 自动化（Windows）或 AppleScript/JXA（macOS）操控 **Adobe Photoshop**，让 AI Agent 直接创建和编辑位图图像。

```bash
cd photoshop-harness/agent-harness
pip install -e .
```

| 命令组 | 功能 |
|--------|------|
| `project` | 新建/打开/保存 PSD 文档 |
| `document` | 文档属性（尺寸、分辨率、色彩模式） |
| `layer` | 图层增删改、可见性、透明度、混合模式 |
| `selection` | 选区操作（全选/羽化/反选/扩展） |
| `image` | 图像调整（裁切、旋转、翻转、画布大小） |
| `text` | 文字图层（字体、大小、颜色） |
| `export` | 导出 PNG / JPEG / WebP / PSD |
| `filter` | 滤镜操作 |

```bash
cli-anything-photoshop project new poster.psd -w 1920 -h 1080
cli-anything-photoshop text add --content "Hello World" --font "Arial" --size 72
cli-anything-photoshop export png result.png
```

**前置条件**：Python 3.10+ + click；Windows 需 pywin32 + Photoshop 2023+；macOS 需 Photoshop 2023+

---

## 安装

### Windows
```bash
pip install git+https://github.com/yb2460/harness-anything-mac.git
pip install pywin32
```

### macOS
```bash
brew install --cask libreoffice
pip install git+https://github.com/yb2460/harness-anything-mac.git
```

### Linux
```bash
sudo apt install libreoffice
pip install git+https://github.com/yb2460/harness-anything-mac.git
```

## 许可证

MIT
