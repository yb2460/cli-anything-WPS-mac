# Photoshop CLI Harness — 软件操作标准 (SOP)

## 软件概述

Adobe Photoshop 是业界标准的位图图像编辑软件。本 harness 通过 Windows COM 自动化接口（`Photoshop.Application`）驱动 Photoshop 2023+。

## 后端架构

```
CLI 命令 → Click CLI 层 → Core 模块 → COM Bridge → Photoshop.Application COM → Photoshop 引擎
```

### 关键设计决策

1. **COM 单例模式**：整个会话共享一个 `Photoshop.Application` 实例，避免重复 Dispatch
2. **状态追踪**：Session 层追踪活跃文档、图层栈、选区状态；支持 undo/redo 快照
3. **原子操作**：每个 CLI 命令映射一个或多个 COM API 调用，保持原子性
4. **JSON 输出**：所有命令支持 `--json` 输出，方便 Agent 解析

## 命令分组

| 命令组 | 描述 | 对应 COM 对象 |
|--------|------|--------------|
| `project` | 新建/打开/保存 PSD 项目 | `Application.Documents` |
| `document` | 文档属性（尺寸、分辨率、色彩模式）| `Document` |
| `layer` | 图层操作（增删改、可见性、透明度、混合模式）| `ArtLayer`, `LayerSet` |
| `selection` | 选区操作（全选、取消、反转、羽化、扩展）| `Selection` |
| `image` | 图像调整（裁切、旋转、翻转、画布大小）| `Document` methods |
| `text` | 文字图层操作（添加/修改文字、字体、大小、颜色）| `ArtLayer.TextItem` |
| `export` | 导出（PNG、JPEG、WebP 等格式）| `Document.Export`, `Document.SaveAs` |
| `filter` | 滤镜操作 | `Document` filter methods |

## 状态模型

```json
{
  "project_path": "path/to/file.psd",
  "active_document": "doc_name",
  "document_info": {
    "width": 1920, "height": 1080, "resolution": 72.0,
    "mode": "RGB", "bits_per_channel": 8
  },
  "layers": [
    {"name": "Background", "type": "pixel", "visible": true, "opacity": 100, "blend_mode": "normal"},
    {"name": "Title", "type": "text", "visible": true, "opacity": 100, "blend_mode": "normal"}
  ],
  "selection": {"active": false, "bounds": null}
}
```

## 错误处理

| 场景 | 行为 |
|------|------|
| Photoshop 未运行 | 自动启动（`Dispatch` 会触发启动） |
| COM 调用失败 | 捕获 `com_error`，输出 JSON 错误，退出码 1 |
| 文件不存在 | 输出明确错误信息 |
| 无活跃文档 | 提示"请先打开或创建项目" |
| 图层名不存在 | 列出所有图层名供参考 |
