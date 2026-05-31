# -*- coding: utf-8 -*-
"""选区操作模块 —— 全选、取消、反转、羽化、扩展、收缩、边界选区。"""
from ..utils.com_bridge import get_bridge


def select_all() -> dict:
    """全选。"""
    bridge = get_bridge()
    doc = bridge.require_document()
    doc.Selection.SelectAll()
    return {"selection": "all", "status": "ok"}


def deselect() -> dict:
    """取消选区。"""
    bridge = get_bridge()
    doc = bridge.require_document()
    doc.Selection.Deselect()
    return {"selection": "none", "status": "ok"}


def invert() -> dict:
    """反转选区。"""
    bridge = get_bridge()
    doc = bridge.require_document()
    doc.Selection.Invert()
    return {"selection": "inverted", "status": "ok"}


def feather(radius: float) -> dict:
    """羽化选区。"""
    bridge = get_bridge()
    doc = bridge.require_document()
    doc.Selection.Feather(radius)
    return {"feather_radius": radius, "status": "ok"}


def expand(pixels: int) -> dict:
    """扩展选区。"""
    bridge = get_bridge()
    doc = bridge.require_document()
    doc.Selection.Expand(pixels)
    return {"expanded_by": pixels, "status": "ok"}


def contract(pixels: int) -> dict:
    """收缩选区。"""
    bridge = get_bridge()
    doc = bridge.require_document()
    doc.Selection.Contract(pixels)
    return {"contracted_by": pixels, "status": "ok"}


def border(width: int) -> dict:
    """选区边界。"""
    bridge = get_bridge()
    doc = bridge.require_document()
    doc.Selection.Border(width)
    return {"border_width": width, "status": "ok"}


def select_bounds(left: int, top: int, right: int, bottom: int) -> dict:
    """按矩形范围创建选区。"""
    bridge = get_bridge()
    doc = bridge.require_document()
    doc.Selection.Select([[left, top], [right, top], [right, bottom], [left, bottom]])
    return {"bounds": [left, top, right, bottom], "status": "ok"}


def fill(color: str = "white", opacity: int = 100) -> dict:
    """填充选区颜色。"""
    bridge = get_bridge()
    doc = bridge.require_document()
    color_map = {
        "white": (255, 255, 255), "black": (0, 0, 0),
        "red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255),
    }
    rgb = color_map.get(color.lower(), (255, 255, 255))
    try:
        from win32com.client import constants
        fill_color = doc.ForegroundColor
        fill_color.RGB = (rgb[2] << 16) | (rgb[1] << 8) | rgb[0]
        doc.Selection.Fill(fill_color)
    except Exception as e:
        raise RuntimeError(f"填充失败: {e}")
    return {"fill": color, "opacity": opacity, "status": "ok"}
