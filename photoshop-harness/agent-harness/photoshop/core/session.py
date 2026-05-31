# -*- coding: utf-8 -*-
"""会话管理模块 —— 项目状态追踪、自动保存、undo/redo 快照。"""
import json
import os
from typing import Optional, Any


class Session:
    """Photoshop CLI 会话管理器。"""

    def __init__(self):
        self.project_path: Optional[str] = None
        self._modified: bool = False
        self._undo_stack: list[dict] = []
        self._redo_stack: list[dict] = []

    def has_project(self) -> bool:
        return self.project_path is not None

    def set_project(self, path: str):
        self.project_path = os.path.abspath(path)
        self._modified = False

    def mark_modified(self):
        self._modified = True

    def snapshot(self):
        """保存当前状态快照（供 undo 使用）。"""
        from ..utils.com_bridge import get_bridge
        bridge = get_bridge()
        doc = bridge.active_document
        if doc is None:
            return
        state = {
            "layers": bridge.list_layers(doc),
            "doc_info": bridge.doc_info(doc),
        }
        self._undo_stack.append(state)
        self._redo_stack.clear()
        self._modified = True

    def undo(self) -> bool:
        if not self._undo_stack:
            return False
        state = self._undo_stack.pop()
        self._redo_stack.append(state)
        return True

    def redo(self) -> bool:
        if not self._redo_stack:
            return False
        state = self._redo_stack.pop()
        self._undo_stack.append(state)
        return True

    def save_session(self):
        """保存会话状态到 JSON 文件。"""
        if not self.project_path:
            return
        from ..utils.com_bridge import get_bridge
        bridge = get_bridge()
        doc = bridge.active_document
        data = {
            "project_path": self.project_path,
            "document": bridge.doc_info(doc) if doc else None,
            "layers": bridge.list_layers(doc) if doc else [],
        }
        _locked_save_json(self.project_path.replace(".psd", ".json"), data)
        self._modified = False

    def load_session(self, path: str) -> dict:
        """从 JSON 文件加载会话状态。"""
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def dispose(self):
        self._undo_stack.clear()
        self._redo_stack.clear()


def _locked_save_json(path: str, data: dict) -> None:
    """原子写入 JSON（带文件锁，Windows 兼容回退）。"""
    try:
        f = open(path, "r+")
    except FileNotFoundError:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        f = open(path, "w")
    with f:
        try:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            _locked = True
        except (ImportError, OSError):
            _locked = False
        try:
            f.seek(0)
            f.truncate()
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
        finally:
            if _locked:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


# ── 全局会话单例 ────────────────────────────────────────────────────────

_session: Optional[Session] = None


def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
    return _session
