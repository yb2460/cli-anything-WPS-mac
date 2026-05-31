# -*- coding: utf-8 -*-
"""Photoshop CLI Harness 单元测试。

测试 ComBridge、Session 及各核心模块的逻辑正确性。
使用 Mock 替代真实 COM 调用，可在无 Photoshop 环境下运行。
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))


class TestComBridge:
    """测试 COM 桥接层。"""

    @patch("cli_anything.photoshop.utils.com_bridge.win32com.client")
    @patch("cli_anything.photoshop.utils.com_bridge.pythoncom")
    def test_singleton(self, mock_pythoncom, mock_win32):
        """ComBridge 是单例模式。"""
        from cli_anything.photoshop.utils.com_bridge import ComBridge
        ComBridge._instance = None  # 重置单例
        b1 = ComBridge()
        b2 = ComBridge()
        assert b1 is b2

    def test_color_modes(self):
        """色彩模式常量映射正确。"""
        from cli_anything.photoshop.utils.com_bridge import COLOR_MODES, COLOR_MODE_NAMES
        assert COLOR_MODES["rgb"] == 2
        assert COLOR_MODES["cmyk"] == 5
        assert COLOR_MODE_NAMES[2] == "RGB"
        assert COLOR_MODE_NAMES[5] == "CMYK"

    def test_blend_modes(self):
        """混合模式列表完整。"""
        from cli_anything.photoshop.utils.com_bridge import BLEND_MODES
        assert "normal" in BLEND_MODES
        assert "multiply" in BLEND_MODES
        assert "overlay" in BLEND_MODES

    def test_export_formats(self):
        """导出格式映射正确。"""
        from cli_anything.photoshop.utils.com_bridge import EXPORT_FORMATS
        assert EXPORT_FORMATS["png"] == 2
        assert EXPORT_FORMATS["jpg"] == 1
        assert EXPORT_FORMATS["gif"] == 4

    def test_anchors(self):
        """锚点位置映射正确。"""
        from cli_anything.photoshop.utils.com_bridge import ANCHORS
        assert ANCHORS["topLeft"] == 1
        assert ANCHORS["middleCenter"] == 5
        assert ANCHORS["bottomRight"] == 9

    def test_get_bridge_global(self):
        """全局 get_bridge 返回单例。"""
        from cli_anything.photoshop.utils.com_bridge import get_bridge, ComBridge
        ComBridge._instance = None
        ComBridge._app = None  # 重置类状态
        with patch.object(ComBridge, "_connect", return_value=None):
            with patch.object(ComBridge, "app", create=True, new_callable=PropertyMock) as mock_app:
                mock_app.return_value = MagicMock()
                b = get_bridge()
                assert isinstance(b, ComBridge)


class TestSession:
    """测试会话管理。"""

    def test_session_singleton(self):
        from cli_anything.photoshop.core.session import Session, get_session, _session
        # 重置全局状态
        import cli_anything.photoshop.core.session as sess_mod
        sess_mod._session = None
        s1 = get_session()
        s2 = get_session()
        assert s1 is s2

    def test_set_project(self):
        from cli_anything.photoshop.core.session import Session
        s = Session()
        s.set_project("/test/file.psd")
        assert s.has_project()
        assert s.project_path.endswith("file.psd")

    def test_mark_modified(self):
        from cli_anything.photoshop.core.session import Session
        s = Session()
        assert not s._modified
        s.mark_modified()
        assert s._modified

    @patch("cli_anything.photoshop.utils.com_bridge.get_bridge")
    def test_undo_redo(self, mock_get_bridge):
        from cli_anything.photoshop.core.session import Session
        s = Session()
        # mock COM bridge 以支持 snapshot
        mock_bridge = MagicMock()
        mock_bridge.active_document = True
        mock_bridge.list_layers.return_value = []
        mock_bridge.doc_info.return_value = {"name": "test"}
        mock_get_bridge.return_value = mock_bridge
        s.snapshot()
        s.snapshot()
        assert s.undo()
        assert s.redo()
        assert not s.redo()  # redo 栈已空

    def test_locked_save_json(self, tmp_path):
        from cli_anything.photoshop.core.session import _locked_save_json
        path = str(tmp_path / "test.json")
        _locked_save_json(path, {"key": "value"})
        assert os.path.exists(path)
        import json
        with open(path, "r") as f:
            assert json.load(f) == {"key": "value"}


class TestLayerModule:
    """测试图层模块的逻辑。"""

    def test_blend_mode_validation(self):
        from cli_anything.photoshop.utils.com_bridge import BLEND_MODES
        assert "normal" in BLEND_MODES
        assert "dissolve" in BLEND_MODES
        assert "unknown_mode" not in BLEND_MODES

    def test_layer_type_constants(self):
        from cli_anything.photoshop.utils.com_bridge import LAYER_TYPES
        assert LAYER_TYPES["pixel"] == 1
        assert LAYER_TYPES["text"] == 2


class TestTextModule:
    """测试文字模块的工具函数。"""

    def test_hex_to_rgb(self):
        from cli_anything.photoshop.core.text import _hex_to_rgb
        assert _hex_to_rgb("#FF0000") == (255, 0, 0)
        assert _hex_to_rgb("#00FF00") == (0, 255, 0)
        assert _hex_to_rgb("#0000FF") == (0, 0, 255)
        assert _hex_to_rgb("#000") == (0, 0, 0)
        assert _hex_to_rgb("FFFFFF") == (255, 255, 255)


class TestExportModule:
    """测试导出模块。"""

    def test_format_validation(self):
        from cli_anything.photoshop.utils.com_bridge import EXPORT_FORMATS
        valid = ["png", "jpg", "gif", "bmp", "tiff", "pdf"]
        for fmt in valid:
            assert fmt in EXPORT_FORMATS, f"格式 {fmt} 应该在导出格式列表中"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
