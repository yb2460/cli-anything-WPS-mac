# Photoshop CLI Harness — 测试计划与结果

## 测试环境

- **OS**: Windows 10/11
- **Python**: 3.10+
- **Photoshop**: 2023+ (COM 已注册)
- **依赖**: pywin32, click, pytest

## 测试范围

### 单元测试 (test_core.py)
- ComBridge 单例模式
- Session 会话状态管理
- 各模块函数正确性（Mock COM 调用）

### E2E 测试 (test_full_e2e.py)
- 完整工作流：创建项目 → 添加图层 → 编辑 → 导出
- 需要 Photoshop 运行

## 单元测试计划

| 测试 | 模块 | 验证内容 |
|------|------|---------|
| test_com_bridge_singleton | utils | 单例模式正确 |
| test_session_project | session | 项目路径设置 |
| test_session_undo | session | 快照/undo/redo 逻辑 |
| test_project_new | project | 创建项目参数传递 |
| test_document_resize | document | 尺寸调整参数 |
| test_layer_add | layer | 图层属性设置 |
| test_selection_all | selection | 选区操作 |
| test_text_add | text | 文字参数 |
| test_export_format | export | 格式检测 |

## E2E 测试计划

| 测试 | 工作流 | 验证 |
|------|--------|------|
| test_full_workflow | new → layer add → text add → export → close | 全流程无错误 |
| test_layer_operations | open → add → duplicate → reorder → delete | 图层操作正确 |
| test_export_formats | new → export png/jpg | 文件生成正确 |
| test_repl_mode | repl 命令执行 | REPL 启动/退出 |

## 测试结果

> 运行 `pytest -v --tb=no` 后填入实际结果。
