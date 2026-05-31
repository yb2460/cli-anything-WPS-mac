# -*- coding: utf-8 -*-
"""Photoshop CLI Harness — E2E 测试。

需要 Photoshop 2023+ 运行。使用子进程方式测试 CLI 命令。
"""
import os
import sys
import json
import subprocess
import shutil
import pytest

# 解决 CLI 安装路径
def _resolve_cli() -> str:
    """查找 cli-anything-photoshop 可执行文件路径。"""
    exe = shutil.which("cli-anything-photoshop")
    if exe:
        return exe
    # 回退：使用模块方式运行
    return [sys.executable, "-m", "cli_anything.photoshop.photoshop_cli"]


CLI = _resolve_cli()
SKIP_E2E = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED") != "1" and not shutil.which("cli-anything-photoshop")


def _run(*args) -> subprocess.CompletedProcess:
    """运行 CLI 命令。"""
    if isinstance(CLI, list):
        cmd = CLI + list(args)
    else:
        cmd = [CLI] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")


def _run_json(*args) -> dict:
    """运行 CLI 命令并解析 JSON 输出。"""
    result = _run("--json", *args)
    if result.returncode != 0:
        return {"error": result.stderr.strip(), "status": "failed"}
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        return {"raw_output": result.stdout.strip(), "status": "parse_error"}


@pytest.mark.skipif(SKIP_E2E, reason="需要安装 cli-anything-photoshop 并运行 Photoshop")
class TestE2EFullWorkflow:
    """完整端到端工作流测试。"""

    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "_e2e_outputs")

    @classmethod
    def setup_class(cls):
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)

    def test_create_project_and_add_layers(self):
        """E2E: 创建项目 → 添加图层 → 添加文字 → 保存。"""
        psd = os.path.join(self.OUTPUT_DIR, "e2e_test.psd")

        # 创建项目
        result = _run_json("project", "new", "-w", "800", "-h", "600", psd)
        assert result.get("width") == 800
        assert result.get("height") == 600

        # 添加图层
        result = _run_json("layer", "add", "-n", "Background", "--type", "pixel")
        assert result.get("name") == "Background"

        # 添加文字
        result = _run_json("text", "add", "-t", "Hello World", "-f", "Arial",
                           "-s", "36", "-c", "#FF0000", "-x", "100", "-y", "200")
        assert "text" in result.get("type", "")

        # 列出图层
        result = _run_json("layer", "list")
        assert isinstance(result, list)
        assert len(result) >= 2

    def test_export_png(self):
        """E2E: 导出为 PNG。"""
        psd = os.path.join(self.OUTPUT_DIR, "e2e_test.psd")
        png = os.path.join(self.OUTPUT_DIR, "e2e_export.png")

        result = _run_json("--project", psd, "export", "save", png, "-f", "png")
        assert result.get("status") == "ok"
        assert os.path.exists(png)
        assert os.path.getsize(png) > 0

    def test_export_jpg(self):
        """E2E: 导出为 JPEG。"""
        psd = os.path.join(self.OUTPUT_DIR, "e2e_test.psd")
        jpg = os.path.join(self.OUTPUT_DIR, "e2e_export.jpg")

        result = _run_json("--project", psd, "export", "save", jpg, "-f", "jpg", "-q", "85")
        assert result.get("status") == "ok"
        assert os.path.exists(jpg)

    def test_document_info(self):
        """E2E: 获取文档信息。"""
        psd = os.path.join(self.OUTPUT_DIR, "e2e_test.psd")
        result = _run_json("--project", psd, "document", "info")
        assert "width" in result
        assert "height" in result

    def test_layer_visibility(self):
        """E2E: 图层可见性控制。"""
        psd = os.path.join(self.OUTPUT_DIR, "e2e_test.psd")
        result = _run_json("--project", psd, "layer", "hide", "-n", "Background")
        assert result.get("visible") is False
        result = _run_json("--project", psd, "layer", "show", "-n", "Background")
        assert result.get("visible") is True

    def test_help_output(self):
        """E2E: 帮助输出。"""
        result = _run("--help")
        assert "Photoshop" in result.stdout
        assert result.returncode == 0


@pytest.mark.skipif(SKIP_E2E, reason="需要安装 cli-anything-photoshop")
class TestCLISubprocess:
    """CLI 子进程测试 — 不依赖 Photoshop COM。"""

    def test_help(self):
        """测试 --help 输出。"""
        result = _run("--help")
        assert result.returncode == 0
        assert "Photoshop" in result.stdout

    def test_json_flag_present(self):
        """--json 标志存在。"""
        result = _run("--help")
        assert "--json" in result.stdout

    def test_dry_run_flag_present(self):
        """--dry-run 标志存在。"""
        result = _run("--help")
        assert "--dry-run" in result.stdout

    def test_project_flag_present(self):
        """--project 标志存在。"""
        result = _run("--help")
        assert "--project" in result.stdout

    def test_all_command_groups(self):
        """所有命令组出现在帮助中。"""
        result = _run("--help")
        assert "project" in result.stdout
        assert "document" in result.stdout
        assert "layer" in result.stdout
        assert "selection" in result.stdout
        assert "text" in result.stdout
        assert "export-group" in result.stdout
        assert "repl" in result.stdout

    def test_project_help(self):
        """子命令帮助。"""
        result = _run("project", "--help")
        assert result.returncode == 0
        assert "new" in result.stdout.lower() or "New" in result.stdout

    def test_layer_help(self):
        """图层子命令帮助。"""
        result = _run("layer", "--help")
        assert result.returncode == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
