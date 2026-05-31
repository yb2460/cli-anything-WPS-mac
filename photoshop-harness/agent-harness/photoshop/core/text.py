# -*- coding: utf-8 -*-
"""文字图层操作模块 —— 添加/修改文字、字体、大小、颜色。"""
from ..utils.com_bridge import get_bridge
from .session import get_session


def add_text(text: str, name: str = None, font: str = "Arial",
             size: float = 24.0, color: str = "#000000",
             x: int = 0, y: int = 0, bold: bool = False,
             italic: bool = False) -> dict:
    """添加文字图层。"""
    bridge = get_bridge()
    doc = bridge.require_document()
    sess = get_session()
    sess.snapshot()

    # 创建文字图层
    layer = doc.ArtLayers.Add()
    layer.Kind = 2  # psTextLayer
    layer.Name = name or f"Text: {text[:20]}"

    text_item = layer.TextItem
    text_item.Contents = text
    text_item.Size = size
    text_item.Font = font
    text_item.Position = [x, y]
    try:
        text_item.Bold = bold
        text_item.Italic = italic
    except Exception:
        pass  # 某些 PS 版本不支持直接设置 Bold/Italic

    # 设置颜色
    try:
        r, g, b = _hex_to_rgb(color)
        color_obj = text_item.Color
        color_obj.RGB.Red = r
        color_obj.RGB.Green = g
        color_obj.RGB.Blue = b
    except Exception:
        pass  # 使用默认颜色

    return bridge._layer_info(layer)


def edit_text(name: str, text: str = None, font: str = None,
              size: float = None, color: str = None,
              bold: bool = None, italic: bool = None) -> dict:
    """编辑文字图层。"""
    bridge = get_bridge()
    layer = bridge.get_layer(name)
    if layer is None:
        raise ValueError(f"文字图层 '{name}' 不存在")
    try:
        text_item = layer.TextItem
    except Exception:
        raise ValueError(f"图层 '{name}' 不是文字图层")

    if text is not None:
        text_item.Contents = text
    if font is not None:
        text_item.Font = font
    if size is not None:
        text_item.Size = size
    if bold is not None:
        try: text_item.Bold = bold
        except Exception: pass
    if italic is not None:
        try: text_item.Italic = italic
        except Exception: pass
    if color is not None:
        r, g, b = _hex_to_rgb(color)
        text_item.Color.RGB.Red = r
        text_item.Color.RGB.Green = g
        text_item.Color.RGB.Blue = b

    return bridge._layer_info(layer)


def get_text_info(name: str = None) -> dict:
    """获取文字图层信息。"""
    bridge = get_bridge()
    if name:
        layer = bridge.get_layer(name)
        if layer is None:
            raise ValueError(f"图层 '{name}' 不存在")
    else:
        layer = bridge.require_document().ActiveLayer
    try:
        ti = layer.TextItem
        return {
            "name": layer.Name,
            "text": ti.Contents,
            "font": ti.Font,
            "size": ti.Size,
            "bold": ti.Bold,
            "italic": ti.Italic,
            "position": list(ti.Position) if ti.Position else None,
        }
    except Exception:
        raise ValueError(f"图层 '{layer.Name}' 不是文字图层")


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """#RRGGBB → (R, G, B)。"""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
