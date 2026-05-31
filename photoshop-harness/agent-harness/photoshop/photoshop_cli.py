# -*- coding: utf-8 -*-
"""Photoshop CLI 入口点 —— Click 命令行工具。

用法:
  cli-anything-photoshop project new --width 1920 --height 1080 output.psd
  cli-anything-photoshop --json layer add -n "Title" --type text
  cli-anything-photoshop --project work.psd export save --format png output.png
  cli-anything-photoshop repl  # 交互式 REPL 模式
"""
import json
import os
import sys
import click

from .core.project import new_project, open_project, save_project, close_project
from .core.document import (resize, canvas_size, crop, rotate, flip,
                             change_mode, trim, get_info)
from .core.layer import (add_layer, delete_layer, duplicate_layer,
                          rename_layer, set_visibility, set_opacity,
                          set_blend_mode, reorder, list_layers, merge_layers)
from .core.selection import (select_all, deselect, invert, feather,
                              expand, contract, border, select_bounds, fill)
from .core.text import add_text, edit_text, get_text_info
from .core.export import export
from .core.session import get_session
from .utils.com_bridge import get_bridge, BLEND_MODES

_repl_mode = False


def _output(data, use_json: bool = False):
    """统一输出：JSON 或表格文本。"""
    if use_json:
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
    elif isinstance(data, list):
        if not data:
            click.echo("(空)")
            return
        # 表格输出
        headers = list(data[0].keys())
        widths = [max(len(h), max((len(str(d.get(h, ""))) for d in data), default=0))
                   for h in headers]
        fmt = "  ".join(f"{{:<{w}}}" for w in widths)
        click.echo(fmt.format(*headers))
        click.echo("  ".join("-" * w for w in widths))
        for row in data:
            click.echo(fmt.format(*[str(row.get(h, "")) for h in headers]))
    elif isinstance(data, dict):
        for k, v in data.items():
            click.echo(f"{k}: {v}")
    else:
        click.echo(str(data))


def _handle_error(func):
    """装饰器：统一错误处理。"""
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            ctx = click.get_current_context()
            use_json = ctx.params.get("use_json", False) if ctx else False
            err = {"error": str(e), "status": "failed"}
            if use_json:
                click.echo(json.dumps(err, ensure_ascii=False), err=True)
            else:
                click.echo(f"✘ 错误: {e}", err=True)
            sys.exit(1)
    return wrapper


# ═══════════════════════════════════════════════════════════════════════════
#  主 CLI 组
# ═══════════════════════════════════════════════════════════════════════════

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True,
              help="以 JSON 格式输出（供 Agent 解析）")
@click.option("--project", "project_path", type=str, default=None,
              help="PSD 项目文件路径")
@click.option("--dry-run", "dry_run", is_flag=True, default=False,
              help="执行命令但不保存到磁盘")
@click.pass_context
def cli(ctx, use_json, project_path, dry_run):
    """CLI-Anything Photoshop —— 通过 COM 自动化操控 Adobe Photoshop。

    所有命令均可通过 --json 输出机器可读的 JSON 格式。
    """
    ctx.ensure_object(dict)
    ctx.obj["use_json"] = use_json
    ctx.obj["dry_run"] = dry_run

    if project_path:
        abs_path = os.path.abspath(project_path)
        if os.path.exists(abs_path):
            open_project(abs_path)
        else:
            new_project(abs_path)

    # 无子命令时输出帮助
    if ctx.invoked_subcommand is None and not _repl_mode:
        click.echo(cli.get_help(ctx))


@cli.result_callback()
def auto_save_on_exit(result, use_json, project_path, dry_run, **kwargs):
    """一 shot 命令后自动保存。"""
    global _repl_mode
    if _repl_mode:
        return
    if dry_run:
        return
    try:
        sess = get_session()
        if sess.has_project() and sess._modified:
            sess.save_session()
    except Exception as e:
        click.echo(f"Warning: 自动保存失败: {e}", err=True)


# ═══════════════════════════════════════════════════════════════════════════
#  project 命令组
# ═══════════════════════════════════════════════════════════════════════════

@cli.group()
def project():
    """项目管理 —— 新建/打开/保存 PSD 文件。"""
    pass


@project.command("new")
@click.option("-w", "--width", type=int, default=1920, help="画布宽度 (px)")
@click.option("-h", "--height", type=int, default=1080, help="画布高度 (px)")
@click.option("-r", "--resolution", type=float, default=72.0, help="分辨率 (PPI)")
@click.option("-m", "--mode", type=str, default="rgb",
              help="色彩模式 (rgb/cmyk/grayscale/lab)")
@click.option("-b", "--bg-color", type=str, default="white",
              help="背景色 (white/black/transparent/red/green/blue)")
@click.argument("path", type=str)
@click.pass_context
@_handle_error
def project_new(ctx, width, height, resolution, mode, bg_color, path):
    """创建新的 PSD 项目。"""
    result = new_project(path, width, height, resolution, mode, bg_color)
    _output(result, ctx.obj.get("use_json"))


@project.command("open")
@click.argument("path", type=str)
@click.pass_context
@_handle_error
def project_open(ctx, path):
    """打开已有 PSD 文件。"""
    result = open_project(path)
    _output(result, ctx.obj.get("use_json"))


@project.command("save")
@click.argument("path", type=str, required=False)
@click.pass_context
@_handle_error
def project_save(ctx, path):
    """保存当前文档。"""
    result = save_project(path)
    _output(result, ctx.obj.get("use_json"))


@project.command("close")
@click.option("--no-save", is_flag=True, help="关闭不保存")
@click.pass_context
@_handle_error
def project_close(ctx, no_save):
    """关闭当前文档。"""
    result = close_project(save=not no_save)
    _output(result, ctx.obj.get("use_json"))


# ═══════════════════════════════════════════════════════════════════════════
#  document 命令组
# ═══════════════════════════════════════════════════════════════════════════

@cli.group()
def document():
    """文档操作 —— 尺寸、分辨率、裁切、旋转、色彩模式。"""
    pass


@document.command("info")
@click.pass_context
@_handle_error
def document_info(ctx):
    """获取当前文档信息。"""
    result = get_info()
    _output(result, ctx.obj.get("use_json"))


@document.command("resize")
@click.option("-w", "--width", type=int, required=True, help="新宽度 (px)")
@click.option("-h", "--height", type=int, required=True, help="新高度 (px)")
@click.option("-r", "--resolution", type=float, help="新分辨率 (PPI)")
@click.pass_context
@_handle_error
def document_resize(ctx, width, height, resolution):
    """调整图像尺寸。"""
    result = resize(width, height, resolution)
    _output(result, ctx.obj.get("use_json"))


@document.command("canvas")
@click.option("-w", "--width", type=int, required=True, help="新画布宽度 (px)")
@click.option("-h", "--height", type=int, required=True, help="新画布高度 (px)")
@click.option("-a", "--anchor", type=str, default="middleCenter",
              help="锚点 (topLeft/topCenter/topRight/middleLeft/middleCenter/...)")
@click.pass_context
@_handle_error
def document_canvas(ctx, width, height, anchor):
    """调整画布大小。"""
    result = canvas_size(width, height, anchor)
    _output(result, ctx.obj.get("use_json"))


@document.command("crop")
@click.option("--left", type=int, required=True)
@click.option("--top", type=int, required=True)
@click.option("--right", type=int, required=True)
@click.option("--bottom", type=int, required=True)
@click.pass_context
@_handle_error
def document_crop(ctx, left, top, right, bottom):
    """裁切图像。"""
    result = crop(left, top, right, bottom)
    _output(result, ctx.obj.get("use_json"))


@document.command("rotate")
@click.option("-a", "--angle", type=float, required=True, help="旋转角度")
@click.pass_context
@_handle_error
def document_rotate(ctx, angle):
    """旋转画布。"""
    result = rotate(angle)
    _output(result, ctx.obj.get("use_json"))


@document.command("flip")
@click.option("-d", "--direction", type=str, default="horizontal",
              help="翻转方向 (horizontal/vertical)")
@click.pass_context
@_handle_error
def document_flip(ctx, direction):
    """翻转画布。"""
    result = flip(direction)
    _output(result, ctx.obj.get("use_json"))


@document.command("mode")
@click.option("-m", "--mode", type=str, required=True,
              help="目标色彩模式 (rgb/cmyk/grayscale/lab/bitmap)")
@click.pass_context
@_handle_error
def document_mode(ctx, mode):
    """更改色彩模式。"""
    result = change_mode(mode)
    _output(result, ctx.obj.get("use_json"))


@document.command("trim")
@click.option("-t", "--type", "trim_type", type=str, default="transparent",
              help="裁切类型 (transparent/topLeft/bottomRight)")
@click.pass_context
@_handle_error
def document_trim(ctx, trim_type):
    """裁切透明/颜色边缘。"""
    result = trim(trim_type)
    _output(result, ctx.obj.get("use_json"))


# ═══════════════════════════════════════════════════════════════════════════
#  layer 命令组
# ═══════════════════════════════════════════════════════════════════════════

@cli.group()
def layer():
    """图层操作 —— 增删改、排序、可见性、透明度、混合模式。"""
    pass


@layer.command("add")
@click.option("-n", "--name", type=str, required=True, help="图层名称")
@click.option("-t", "--type", "layer_type", type=str, default="pixel",
              help="图层类型 (pixel/text)")
@click.option("-o", "--opacity", type=int, default=100, help="透明度 (0-100)")
@click.option("-b", "--blend-mode", type=str, default="normal",
              help=f"混合模式 ({', '.join(BLEND_MODES[:8])}…)")
@click.option("-g", "--group", type=str, help="放入图层组")
@click.pass_context
@_handle_error
def layer_add(ctx, name, layer_type, opacity, blend_mode, group):
    """添加新图层。"""
    result = add_layer(name, layer_type, opacity, blend_mode, group)
    _output(result, ctx.obj.get("use_json"))


@layer.command("delete")
@click.option("-n", "--name", type=str, required=True, help="图层名称")
@click.pass_context
@_handle_error
def layer_delete(ctx, name):
    """删除图层。"""
    result = delete_layer(name)
    _output(result, ctx.obj.get("use_json"))


@layer.command("duplicate")
@click.option("-n", "--name", type=str, required=True, help="源图层名称")
@click.option("--new-name", type=str, help="新图层名称")
@click.pass_context
@_handle_error
def layer_duplicate(ctx, name, new_name):
    """复制图层。"""
    result = duplicate_layer(name, new_name)
    _output(result, ctx.obj.get("use_json"))


@layer.command("rename")
@click.option("--old", type=str, required=True, help="当前名称")
@click.option("--new", "new_name", type=str, required=True, help="新名称")
@click.pass_context
@_handle_error
def layer_rename(ctx, old, new_name):
    """重命名图层。"""
    result = rename_layer(old, new_name)
    _output(result, ctx.obj.get("use_json"))


@layer.command("show")
@click.option("-n", "--name", type=str, required=True, help="图层名称")
@click.pass_context
@_handle_error
def layer_show(ctx, name):
    """显示图层。"""
    result = set_visibility(name, True)
    _output(result, ctx.obj.get("use_json"))


@layer.command("hide")
@click.option("-n", "--name", type=str, required=True, help="图层名称")
@click.pass_context
@_handle_error
def layer_hide(ctx, name):
    """隐藏图层。"""
    result = set_visibility(name, False)
    _output(result, ctx.obj.get("use_json"))


@layer.command("opacity")
@click.option("-n", "--name", type=str, required=True, help="图层名称")
@click.option("-o", "--opacity", type=int, required=True, help="透明度 (0-100)")
@click.pass_context
@_handle_error
def layer_opacity(ctx, name, opacity):
    """设置图层透明度。"""
    result = set_opacity(name, opacity)
    _output(result, ctx.obj.get("use_json"))


@layer.command("blend")
@click.option("-n", "--name", type=str, required=True, help="图层名称")
@click.option("-m", "--mode", type=str, required=True,
              help=f"混合模式 ({', '.join(BLEND_MODES[:8])}…)")
@click.pass_context
@_handle_error
def layer_blend(ctx, name, mode):
    """设置图层混合模式。"""
    result = set_blend_mode(name, mode)
    _output(result, ctx.obj.get("use_json"))


@layer.command("list")
@click.option("--json", "use_json", is_flag=True, help="JSON 输出")
@click.pass_context
@_handle_error
def layer_list(ctx, use_json):
    """列出所有图层。"""
    result = list_layers()
    _output(result, use_json or ctx.obj.get("use_json"))


@layer.command("reorder")
@click.option("-n", "--name", type=str, required=True, help="图层名称")
@click.option("-p", "--position", type=int, required=True, help="目标位置 (1=最底)")
@click.pass_context
@_handle_error
def layer_reorder(ctx, name, position):
    """调整图层顺序。"""
    result = reorder(name, position)
    _output(result, ctx.obj.get("use_json"))


@layer.command("merge")
@click.option("-n", "--name", type=str, required=True, help="要合并的图层")
@click.option("--with-layer", type=str, help="与指定图层合并（不指定则向下合并）")
@click.pass_context
@_handle_error
def layer_merge(ctx, name, with_layer):
    """合并图层。"""
    result = merge_layers(name, with_layer)
    _output(result, ctx.obj.get("use_json"))


# ═══════════════════════════════════════════════════════════════════════════
#  selection 命令组
# ═══════════════════════════════════════════════════════════════════════════

@cli.group()
def selection():
    """选区操作 —— 全选、取消、反转、羽化、填充。"""
    pass


@selection.command("all")
@click.pass_context
@_handle_error
def selection_all(ctx):
    """全选。"""
    result = select_all()
    _output(result, ctx.obj.get("use_json"))


@selection.command("none")
@click.pass_context
@_handle_error
def selection_none(ctx):
    """取消选区。"""
    result = deselect()
    _output(result, ctx.obj.get("use_json"))


@selection.command("invert")
@click.pass_context
@_handle_error
def selection_invert(ctx):
    """反转选区。"""
    result = invert()
    _output(result, ctx.obj.get("use_json"))


@selection.command("feather")
@click.option("-r", "--radius", type=float, required=True, help="羽化半径")
@click.pass_context
@_handle_error
def selection_feather(ctx, radius):
    """羽化选区。"""
    result = feather(radius)
    _output(result, ctx.obj.get("use_json"))


@selection.command("expand")
@click.option("-p", "--pixels", type=int, required=True, help="扩展像素数")
@click.pass_context
@_handle_error
def selection_expand(ctx, pixels):
    """扩展选区。"""
    result = expand(pixels)
    _output(result, ctx.obj.get("use_json"))


@selection.command("contract")
@click.option("-p", "--pixels", type=int, required=True, help="收缩像素数")
@click.pass_context
@_handle_error
def selection_contract(ctx, pixels):
    """收缩选区。"""
    result = contract(pixels)
    _output(result, ctx.obj.get("use_json"))


@selection.command("border")
@click.option("-w", "--width", type=int, required=True, help="边框宽度")
@click.pass_context
@_handle_error
def selection_border(ctx, width):
    """选区边界。"""
    result = border(width)
    _output(result, ctx.obj.get("use_json"))


@selection.command("rect")
@click.option("--left", type=int, required=True)
@click.option("--top", type=int, required=True)
@click.option("--right", type=int, required=True)
@click.option("--bottom", type=int, required=True)
@click.pass_context
@_handle_error
def selection_rect(ctx, left, top, right, bottom):
    """按矩形范围创建选区。"""
    result = select_bounds(left, top, right, bottom)
    _output(result, ctx.obj.get("use_json"))


@selection.command("fill")
@click.option("-c", "--color", type=str, default="white",
              help="填充颜色 (white/black/red/green/blue)")
@click.option("-o", "--opacity", type=int, default=100, help="不透明度 (0-100)")
@click.pass_context
@_handle_error
def selection_fill(ctx, color, opacity):
    """填充选区。"""
    result = fill(color, opacity)
    _output(result, ctx.obj.get("use_json"))


# ═══════════════════════════════════════════════════════════════════════════
#  text 命令组
# ═══════════════════════════════════════════════════════════════════════════

@cli.group()
def text():
    """文字操作 —— 添加/修改文字图层、字体、大小、颜色。"""
    pass


@text.command("add")
@click.option("-t", "--text", type=str, required=True, help="文字内容")
@click.option("-n", "--name", type=str, help="图层名称")
@click.option("-f", "--font", type=str, default="Arial", help="字体名称")
@click.option("-s", "--size", type=float, default=24.0, help="字号 (pt)")
@click.option("-c", "--color", type=str, default="#000000", help="文字颜色（十六进制）")
@click.option("-x", type=int, default=0, help="X 位置")
@click.option("-y", type=int, default=0, help="Y 位置")
@click.option("--bold/--no-bold", default=False)
@click.option("--italic/--no-italic", default=False)
@click.pass_context
@_handle_error
def text_add(ctx, text, name, font, size, color, x, y, bold, italic):
    """添加文字图层。"""
    result = add_text(text, name, font, size, color, x, y, bold, italic)
    _output(result, ctx.obj.get("use_json"))


@text.command("edit")
@click.option("-n", "--name", type=str, required=True, help="图层名称")
@click.option("-t", "--text", type=str, help="新文字内容")
@click.option("-f", "--font", type=str, help="新字体")
@click.option("-s", "--size", type=float, help="新字号")
@click.option("-c", "--color", type=str, help="新颜色（十六进制）")
@click.option("--bold/--no-bold", default=None)
@click.option("--italic/--no-italic", default=None)
@click.pass_context
@_handle_error
def text_edit(ctx, name, text, font, size, color, bold, italic):
    """编辑文字图层。"""
    result = edit_text(name, text, font, size, color, bold, italic)
    _output(result, ctx.obj.get("use_json"))


@text.command("info")
@click.option("-n", "--name", type=str, help="图层名称（不指定则用当前活跃图层）")
@click.pass_context
@_handle_error
def text_info(ctx, name):
    """获取文字图层信息。"""
    result = get_text_info(name)
    _output(result, ctx.obj.get("use_json"))


# ═══════════════════════════════════════════════════════════════════════════
#  export 命令组
# ═══════════════════════════════════════════════════════════════════════════

@cli.group()
def export_group():
    """导出 —— 将 PSD 导出为 PNG、JPEG、WebP 等格式。"""
    pass


@export_group.command("save")
@click.argument("path", type=str)
@click.option("-f", "--format", "fmt", type=str,
              help="导出格式 (png/jpg/bmp/gif/tiff/pdf)")
@click.option("-q", "--quality", type=int, default=90, help="JPEG 质量 (0-100)")
@click.option("-w", "--width", type=int, help="导出宽度 (px)")
@click.option("-h", "--height", type=int, help="导出高度 (px)")
@click.pass_context
@_handle_error
def export_save(ctx, path, fmt, quality, width, height):
    """导出为指定格式。"""
    result = export(path, fmt, quality, width, height)
    _output(result, ctx.obj.get("use_json"))


# ═══════════════════════════════════════════════════════════════════════════
#  repl 命令
# ═══════════════════════════════════════════════════════════════════════════

@cli.command()
@click.option("--json", "use_json", is_flag=True, help="REPL 输出 JSON 格式")
@click.pass_context
def repl(ctx, use_json):
    """启动交互式 REPL 模式。"""
    global _repl_mode
    _repl_mode = True

    click.echo("╔════════════════════════════════════════════════════════╗")
    click.echo("║   CLI-Anything Photoshop REPL  v1.0.0                  ║")
    click.echo("║   输入命令或 'help' 查看帮助，'quit' 退出              ║")
    click.echo("╚════════════════════════════════════════════════════════╝")

    while True:
        try:
            line = input("ps> ").strip()
        except (EOFError, KeyboardInterrupt):
            click.echo("\n退出。")
            break

        if not line:
            continue
        if line.lower() in ("quit", "exit", "q"):
            break
        if line.lower() == "help":
            click.echo(cli.get_help(ctx))
            continue
        if line.lower() == "layers":
            result = list_layers()
            _output(result, use_json)
            continue
        if line.lower() == "info":
            result = get_info()
            _output(result, use_json)
            continue

        # 将输入转为 argparse 风格传给 Click
        try:
            args = line.split()
            # 支持 REPL 快捷命令
            ctx.obj["use_json"] = use_json
            cli(args, standalone_mode=False)
        except SystemExit:
            pass  # 吞掉 sys.exit
        except Exception as e:
            click.echo(f"✘ 错误: {e}", err=True)

    # 清理
    try:
        get_bridge().dispose()
    except Exception:
        pass
    click.echo("会话结束。")


# ═══════════════════════════════════════════════════════════════════════════
#  入口
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """CLI 入口。"""
    cli(standalone_mode=True)


if __name__ == "__main__":
    main()
