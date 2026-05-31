# -*- coding: utf-8 -*-
"""文档操作模块 —— 调整文档尺寸、分辨率、色彩模式、裁切等。"""
from ..utils.com_bridge import get_bridge, COLOR_MODES


def resize(width: int, height: int, resolution: float = None) -> dict:
    """调整图像大小。"""
    bridge = get_bridge()
    doc = bridge.require_document()
    res = resolution or doc.Resolution
    doc.ResizeImage(width, height, res)
    return bridge.doc_info(doc)


def canvas_size(width: int, height: int, anchor: str = "middleCenter") -> dict:
    """调整画布大小。"""
    bridge = get_bridge()
    doc = bridge.require_document()
    from ..utils.com_bridge import ANCHORS
    anchor_pos = ANCHORS.get(anchor, 5)
    doc.ResizeCanvas(width, height, anchor_pos)
    return bridge.doc_info(doc)


def crop(left: int, top: int, right: int, bottom: int) -> dict:
    """裁切图像。"""
    bridge = get_bridge()
    doc = bridge.require_document()
    doc.Crop([left, top, right, bottom])
    return bridge.doc_info(doc)


def rotate(angle: float) -> dict:
    """旋转画布（角度）。"""
    bridge = get_bridge()
    doc = bridge.require_document()
    doc.RotateCanvas(angle)
    return bridge.doc_info(doc)


def flip(direction: str = "horizontal") -> dict:
    """翻转画布。"""
    bridge = get_bridge()
    doc = bridge.require_document()
    if direction == "horizontal":
        doc.FlipCanvas(1)  # psHorizontal
    elif direction == "vertical":
        doc.FlipCanvas(2)  # psVertical
    else:
        raise ValueError(f"无效翻转方向: {direction}，可选: horizontal, vertical")
    return bridge.doc_info(doc)


def change_mode(mode: str) -> dict:
    """更改色彩模式。"""
    bridge = get_bridge()
    doc = bridge.require_document()
    mode_id = COLOR_MODES.get(mode.lower())
    if mode_id is None:
        raise ValueError(f"无效色彩模式: {mode}，可选: {list(COLOR_MODES.keys())}")
    doc.ChangeMode(mode_id)
    return bridge.doc_info(doc)


def trim(trim_type: str = "transparentPixels") -> dict:
    """裁切透明/颜色边缘。"""
    bridge = get_bridge()
    doc = bridge.require_document()
    type_map = {"transparent": 1, "topLeft": 2, "bottomRight": 3}
    doc.Trim(type_map.get(trim_type, 1))
    return bridge.doc_info(doc)


def get_info() -> dict:
    """获取文档信息。"""
    bridge = get_bridge()
    return bridge.doc_info()
