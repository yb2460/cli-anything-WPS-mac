---
name: "cli-anything-photoshop"
description: "通过 COM 自动化操控 Adobe Photoshop 的 CLI harness。支持项目管理、图层操作、选区控制、文字编辑、图像调整和多格式导出。"
---

# CLI-Anything Photoshop

通过 Windows COM 自动化接口操控 Adobe Photoshop 的命令行工具。

## 前置条件

- **Windows 10/11**
- **Adobe Photoshop 2023+** (需注册 COM 接口)
- **Python 3.10+** 及 `pywin32` 包

## 安装

```bash
cd photoshop-harness/agent-harness
pip install -e .
```

安装后可使用 `cli-anything-photoshop` 命令。

## 命令结构

```
cli-anything-photoshop [--json] [--project <path>] [--dry-run] <command-group> <command> [options]
```

### 全局选项

| 选项 | 描述 |
|------|------|
| `--json` | 以 JSON 格式输出（供 AI Agent 解析） |
| `--project <path>` | 自动打开或创建 PSD 项目文件 |
| `--dry-run` | 执行命令但不保存到磁盘 |

## 命令组

### project — 项目管理
| 命令 | 选项 | 描述 |
|------|------|------|
| `new <path>` | `-w` width, `-h` height, `-r` resolution, `-m` mode, `-b` bg-color | 创建新 PSD |
| `open <path>` | | 打开 PSD 文件 |
| `save [path]` | | 保存文档 |
| `close` | `--no-save` | 关闭文档 |

### document — 文档操作
| 命令 | 选项 | 描述 |
|------|------|------|
| `info` | | 文档信息 |
| `resize` | `-w` width, `-h` height, `-r` resolution | 调整尺寸 |
| `canvas` | `-w` width, `-h` height, `-a` anchor | 调整画布 |
| `crop` | `--left --top --right --bottom` | 裁切 |
| `rotate` | `-a` angle | 旋转画布 |
| `flip` | `-d` direction | 翻转画布 |
| `mode` | `-m` mode | 更改色彩模式 |
| `trim` | `-t` type | 裁切边缘 |

### layer — 图层操作
| 命令 | 选项 | 描述 |
|------|------|------|
| `add` | `-n` name, `-t` type, `-o` opacity, `-b` blend | 添加图层 |
| `delete` | `-n` name | 删除图层 |
| `duplicate` | `-n` name, `--new-name` name | 复制图层 |
| `rename` | `--old` name, `--new` name | 重命名 |
| `show` / `hide` | `-n` name | 显示/隐藏 |
| `opacity` | `-n` name, `-o` opacity | 设置透明度 |
| `blend` | `-n` name, `-m` mode | 设置混合模式 |
| `list` | | 列出所有图层 |
| `reorder` | `-n` name, `-p` position | 调整顺序 |
| `merge` | `-n` name, `--with-layer` name | 合并图层 |

### selection — 选区操作
| 命令 | 选项 | 描述 |
|------|------|------|
| `all` | | 全选 |
| `none` | | 取消选区 |
| `invert` | | 反转选区 |
| `feather` | `-r` radius | 羽化 |
| `expand` | `-p` pixels | 扩展 |
| `contract` | `-p` pixels | 收缩 |
| `border` | `-w` width | 边框选区 |
| `rect` | `--left --top --right --bottom` | 矩形选区 |
| `fill` | `-c` color, `-o` opacity | 填充选区 |

### text — 文字操作
| 命令 | 选项 | 描述 |
|------|------|------|
| `add` | `-t` text, `-f` font, `-s` size, `-c` color | 添加文字 |
| `edit` | `-n` name, `-t` text, `-f` font, `-s` size, `-c` color | 编辑文字 |
| `info` | `-n` name | 文字信息 |

### export — 导出
| 命令 | 选项 | 描述 |
|------|------|------|
| `save <path>` | `-f` format, `-q` quality, `-w` width, `-h` height | 导出文件 |

### repl
| 命令 | 描述 |
|------|------|
| `repl` | 启动交互式 REPL 模式 |

## 使用示例

### AI Agent 用法（--json 模式）

```bash
# 创建新项目并获取 JSON 输出
cli-anything-photoshop --json project new -w 800 -h 600 poster.psd

# 添加文字图层
cli-anything-photoshop --json --project poster.psd text add -t "Hello World" -f Arial -s 48 -c "#FF0000"

# 列出所有图层（JSON 格式）
cli-anything-photoshop --json --project poster.psd layer list

# 导出为 PNG
cli-anything-photoshop --json --project poster.psd export save -f png output.png

# 预览（不保存）
cli-anything-photoshop --dry-run --project poster.psd layer add -n "draft" --type text
```

### 人工使用

```bash
# 打开 PSD，交互编辑
cli-anything-photoshop --project work.psd layer list

# 启动 REPL
cli-anything-photoshop repl
```

## Agent 使用指南

1. **始终使用 `--json` 标志** 获取结构化输出
2. **使用 `--dry-run` 预览**，确认后再正式保存
3. **错误处理**：退出码非零时检查 `stderr` 中的 JSON 错误对象
4. **项目状态**：使用 `--project` 自动管理文件打开/保存
5. **REPL 模式**：适合多步骤交互式操作，减少 Photoshop 进程启动开销

## Photoshop COM 架构

```
CLI 命令 → Click CLI → Core 模块 → ComBridge (单例) → Photoshop.Application COM → Photoshop 引擎
```

Photoshop 通过 Windows COM 接口暴露全部编辑能力。本 harness 封装了最常用的操作。如需扩展，参考 Adobe Photoshop COM 文档添加新方法到 `utils/com_bridge.py`。
