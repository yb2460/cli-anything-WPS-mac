# cli-anything-WPS-mac

<h3 align="center">跨平台 Office 自动化 —— Windows 用 WPS，Mac/Linux 用 LibreOffice</h3>

<p align="center">
  <img src="https://img.shields.io/badge/平台-Windows%20%7C%20macOS%20%7C%20Linux-blue" alt="Platform">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/协议-MIT-green" alt="License">
</p>

---

## 这是什么

一个跨平台命令行工具，让 AI Agent 操控 Office 软件完成文档创建、编辑和导出。

- **Windows 上** → 通过 COM 接口操控 WPS Office
- **macOS / Linux 上** → 通过 headless 模式操控 LibreOffice

同样的命令，任何平台都能跑。

## 安装

### Windows（需要 WPS Office）

```bash
pip install git+https://github.com/yb2460/cli-anything-WPS-mac.git
pip install pywin32
```

### macOS（需要 LibreOffice）

```bash
brew install --cask libreoffice
pip install git+https://github.com/yb2460/cli-anything-WPS-mac.git
```

### Linux

```bash
sudo apt install libreoffice
pip install git+https://github.com/yb2460/cli-anything-WPS-mac.git
```

### 验证

```bash
cli-anything-office --help
```

## 快速上手

```bash
cli-anything-office document new --type writer --name "报告" -o report.json
cli-anything-office --project report.json writer add-paragraph -t "AI 生成的文字。"
cli-anything-office --project report.json export render report.pdf -p pdf
```

## 新增：PPT 设计风格系统

整合 4 个专业 PPT Skill 的设计精华，内置：

**4 套设计预设**

| 预设 | 风格 | 适用场景 |
|------|------|---------|
| `academic` | 学术答辩 | 会议报告、论文答辩、基金申请 |
| `consultant` | 咨询顾问 | 商业计划书、咨询报告 |
| `business` | 商务汇报 | 会议汇报、项目提案、教学课件 |
| `tech` | 科技极简 | 产品发布、AI 演示、数据报告 |

**14 种布局模板 + 4 种演讲类型 + 5 维度质量审查**

```bash
cli-anything-office preset list              # 查看所有预设
cli-anything-office preset apply academic    # 应用学术风格
```

## 支持的操作

| Writer | Calc | Impress |
|--------|------|---------|
| 段落、标题、列表 | 工作表增删改 | 幻灯片增删改 |
| 表格、图片、分页 | 单元格读写、公式 | 文本框、形状 |
| 字体/字号/颜色 | 合并、批量填充 | 背景、布局 |
| 导出 DOCX/PDF/TXT | 导出 XLSX/CSV/PDF | 导出 PPTX/PDF |

## 系统要求

| Windows | macOS | Linux |
|---------|-------|-------|
| WPS Office 2019+ | LibreOffice 7+ | LibreOffice 7+ |
| Python 3.10+ pywin32 | Python 3.10+ | Python 3.10+ |

## 原理

```
CLI 命令 (跨平台统一)
    ↓
platform detection
   ╱           ╲
Windows       macOS/Linux
  WPS COM     LibreOffice headless
```

## 运行测试

```bash
pip install -e .[dev]
python -m pytest cli_anything/office/tests/ -v
```

## 许可证

MIT
