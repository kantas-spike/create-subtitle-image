import inkex
import json
import os
import argparse
from tempfile import TemporaryDirectory
from datetime import datetime, timedelta
import json
import re


def time_to_delta(t):
    return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)


def read_srt_file(path):
    item_list = []
    with open(path, encoding="utf-8") as f:
        item = {}
        for line_with_sep in f:
            line = line_with_sep.rstrip(os.linesep)
            if len(line) == 0:
                if len(item) > 0:
                    item_list.append(item)
                    item = {}
            elif len(item) == 0:
                item["no"] = int(line)
            elif len(item) == 1:
                if "-->" not in line:
                    raise ValueError(f"Bad time format:{item}")
                item["time_info"] = parse_line_of_time(line)
            elif len(item) == 2:
                item["lines"] = []
                item["lines"].append(line)
            elif len(item) == 3:
                item["lines"].append(line)

        if len(item) > 0:
            item_list.append(item)

    return item_list


def parse_line_of_time(line):
    m = re.match(r"\A(\d+:\d+:\d+,\d+) *--> *(\d+:\d+:\d+,\d+) *(.+)?", line)
    results = {}
    if m:
        for k, t in [["start", m.group(1)], ["end", m.group(2)]]:
            if t:
                results[k] = time_to_delta(datetime.strptime(t, "%H:%M:%S,%f"))
            else:
                results[k] = None
        if m.group(3):
            extras = m.group(3)
            if "JSON:" in extras:
                json_data = json.loads(extras.split("JSON:")[1].strip())
                results["json"] = json_data
        return results
    else:
        return results


def inkscape_run_command_with_actions(svg, *options):
    with TemporaryDirectory(prefix="inkscape_command_with_actions") as tmpdir:
        svg_file = inkex.command.write_svg(svg, tmpdir, "input.svg")
        inkex.command.inkscape(svg_file, batch_process=True, *options)


def export_to_png(export_path, id=None):
    options = [['export-area-drawing', True], ['export-type', 'png'],
               ['export-filename', os.path.abspath(os.path.expanduser(export_path))]]

    if id is not None:
        options.append(['export-id-only', True], ['export-id', id])

    inkscape_run_command_with_actions(svg_root, *options)


def apply_path_effect(grp, lpe):
    # Convert a scalar to a singleton list for consistent access.
    if isinstance(lpe, list):
        lpe_list = lpe
    else:
        lpe_list = [lpe]

    # Rename the d attribute to inkscape:original-d to notify Inkscape
    # to compute the modified d.

    for path in grp:
        obj = path._inkscape_obj
        d = obj.get('d')
        if d is not None:
            obj.set('inkscape:original-d', d)
            obj.set('d', None)

    # Apply each LPE in turn.
    for one_lpe in lpe_list:
        obj_grp = grp._inkscape_obj
        # If this is our first LPE, apply it.  Otherwise, append it to the
        # previous LPE.
        pe_list = obj_grp.get('inkscape:path-effect')
        if pe_list is None:
            obj_grp.set('inkscape:path-effect', str(one_lpe))
        else:
            obj_grp.set('inkscape:path-effect', '%s;%s' %
                        (pe_list, str(one_lpe)))


def remove_objects(*objs):
    for o in objs:
        _simple_top.remove_obj(o)


def export_text_to_path(text, combine=True):
    obj = text.get_inkex_object()
    svg = obj.root
    obj_id = obj.get_id()
    with TemporaryDirectory(prefix="inkscape_command_with_actions") as tmpdir:
        svg_file = inkex.command.write_svg(
            svg, tmpdir, "input_for_text_to_path.svg")
        output_path = os.path.join(tmpdir, "output_for_text_to_path.svg")
        options = [['export-text-to-path', True], ['export-id', obj_id],
                   ['export-id-only', True], ['export-filename', output_path]]
        inkex.command.inkscape(svg_file, batch_process=True, *options)
        objs = objects_from_svg_file(output_path)
        if combine:
            p_list = objs[0].ungroup()
            path = p_list.pop(0)
            for p in p_list:
                path.append(p)
            return path
        else:
            return objs[0]


def create_text_group(texts, base=[0, 0], line_sep=1.1, **styles):
    txt_obj = None
    font_size = DEFAULT_FONT_SIZE * pt
    if 'font_size' in styles:
        font_size = styles['font_size']

    for t in texts:
        if txt_obj is None:
            txt_obj = text(t, base, **styles)
        else:
            txt_obj.add_text(t, base, **styles)

        base[1] += font_size * line_sep

    return txt_obj


def expand_path(path, base_dir):
    epd_path = os.path.expanduser(path)
    if os.path.isabs(epd_path):
        return epd_path
    else:
        epd_base_dir = os.path.abspath(os.path.expanduser(base_dir))
        return os.path.abspath(os.path.join(epd_base_dir, epd_path))


def create_shadow_filter(shadow_color, opacity=0.3, stdDeviation=3.125, dx=2.33645, dy=2.33645):
    filter7285 = filter_effect(name='Drop Shadow', color_interpolation_filters='sRGB')
    flood = filter7285.add('Flood', flood_opacity=opacity, flood_color=shadow_color)
    composite1 = filter7285.add('Composite', src1=flood, src2='SourceGraphic', operator='in')
    filter7285.add('GaussianBlur', src1=composite1, stdDeviation=stdDeviation)
    offset = filter7285.add('Offset', dx=dx, dy=dy)
    filter7285.add('Composite', src1='SourceGraphic', src2=offset, operator='over')
    return filter7285


def create_box(bb, color, opacity=0.3, margin_x=0, margin_y=0):
    # print(bb, margin_x, margin_y)
    return rect((bb.left - margin_x, bb.top - margin_y), (bb.right + margin_x, bb.bottom + margin_y), fill=color, opacity=opacity, stroke_width=0)


DEFAULT_FONT_SIZE = 48
DEFAULT_FONT_FAMILY = "BIZ UDGothic"
DEFAULT_FONT_STYLE = "normal"
DEFAULT_TEXT_ANCHOR = "middle"
DEFAULT_LINE_SEP = 1.1
COLOR_WHITE = "#000000"
COLOR_BLACK = "#FFFFFF"
DEFAULT_OFFSET_RATE = 0.06
DEFAULT_OFFSET_STROKE_RATE = 0.03
DEFAULT_BASE_DIR = os.path.expanduser("~")
DEFAULT_BOX_MARGIN_X = 0.5
DEFAULT_BOX_MARGIN_Y = 0.25
DEFAULT_BOX_OPACITY = 0.3
DEFAULT_SHADOW_OPACITY = 0.3
DEFAULT_SHADOW_BLUR = 1.5
DEFAULT_SHADOW_DX = 1.5
DEFAULT_SHADOW_DY = 1.5

settings = {
    "font_size": DEFAULT_FONT_SIZE,
    "font_family": DEFAULT_FONT_FAMILY,
    "font_style": DEFAULT_FONT_STYLE,
    "text_color": COLOR_BLACK,
    "text_anchor": DEFAULT_TEXT_ANCHOR,
    "line_sep": DEFAULT_LINE_SEP,
    "offset_rate": DEFAULT_OFFSET_RATE,
    "offset_stroke_rate": DEFAULT_OFFSET_STROKE_RATE,
    "offset_color": COLOR_WHITE,
    "base_dir": DEFAULT_BASE_DIR,
    "box_margin_x": DEFAULT_BOX_MARGIN_X,
    "box_margin_y": DEFAULT_BOX_MARGIN_Y,
    "box_opacity": DEFAULT_BOX_OPACITY,
    "shadow_opacity": DEFAULT_SHADOW_OPACITY,
    "shadow_blur_stddeviation": DEFAULT_SHADOW_BLUR,
    "shadow_dx": DEFAULT_SHADOW_DX,
    "shadow_dy": DEFAULT_SHADOW_DY,
}

parser = argparse.ArgumentParser(prog="create-subtitle-image")
parser.add_argument("--font-size", type=float, default=settings['font_size'],
                    help=f"字幕テキストのフォントサイズ(単位:pt). (デフォルト値: {settings['font_size']})")
parser.add_argument("--font-family", type=str, default=settings['font_family'],
                    help=f"字幕テキストのフォントファミリー. (デフォルト値: {settings['font_family']})")
parser.add_argument("--font-style", type=str, default=settings['font_style'],
                    help=f"字幕テキストのフォントのスタイル. (デフォルト値: {settings['font_style']})")
parser.add_argument("--text-anchor", choices=("start", "middle", "end"),
                    type=str, default=settings['text_anchor'], help=f"テキストのアンカー. (デフォルト値: {settings['text_anchor']})")
parser.add_argument("--line-sep", type=float, default=settings['line_sep'],
                    help=f"字幕テキストの行間. (デフォルト値: {settings['line_sep']})")
parser.add_argument("--text-color", type=str,
                    default=settings['text_color'], help=f"テキストの色. (デフォルト値: {settings['text_color']})")
parser.add_argument("--letter-spacing", type=float, default=None, help="文字の間隔. (デフォルト値: なし)")
parser.add_argument("--offset-rate", type=float,
                    default=settings['offset_rate'], help=f"縁取り用に拡大する割合.基準はフォントサイズ. (デフォルト値: {settings['offset_rate']})")
parser.add_argument("--offset-color", type=str,
                    default=settings['offset_color'], help=f"縁取りの色. (デフォルト値: {settings['offset_color']})")
parser.add_argument("--offset-stroke", type=str, default=None,
                    help="縁取りの枠線の色.色未指定の場合は枠線を表示しない. (デフォルト値: なし)")
parser.add_argument("--offset-stroke-rate", type=float, default=settings['offset_stroke_rate'],
                    help=f"縁取りの枠線の幅.基準はフォントサイズ. (デフォルト値: {settings['offset_stroke_rate']})")
parser.add_argument("--shadow-color", type=str, default=None,
                    help="影の色.色未指定の場合は影を表示しない. (デフォルト値: なし)")
parser.add_argument("--box-color", type=str, default=None,
                    help="背景色.色未指定の場合は背景を塗り潰さない. (デフォルト値: なし)")
parser.add_argument("--export-ids", type=int, nargs='*', default=[], help="出力する字幕番号. 未指定時は全ての字幕を出力する")
parser.add_argument("--srt-path", type=str, required=True, help="字幕ファイルのパス")
parser.add_argument("--config-path", type=str, help="設定ファイル(json形式)のパス")
parser.add_argument("--export-dir", type=str, required=True, help="作成した字幕画像の出力先dir.")
parser.add_argument("--base-dir", type=str, default=settings['base_dir'],
                    help=f"相対パスを絶対パスに変換する際に基準とするディレクトリ. (デフォルト値: {settings['base_dir']})")

args = parser.parse_args(user_args)
print(args)
settings.update(vars(args))

if args.config_path:
    config_path = expand_path(args.config_path, settings["base_dir"])
    with open(config_path) as f:
        config = json.load(f)
        settings.update(config)

# print(settings)

srt_path = expand_path(args.srt_path, settings["base_dir"])
export_dir = expand_path(settings["export_dir"], settings["base_dir"])

print("srt_file: ", srt_path, "export_dir: ", export_dir)

# print(args, srt_path, export_dir)
if not os.path.isdir(export_dir):
    os.makedirs(export_dir)

items = read_srt_file(srt_path)
offset_size = settings["offset_rate"] * settings["font_size"]
letter_spacing = 0
if settings["letter_spacing"] is None:
    if offset_size > 0:
        settings["letter_spacing"] = offset_size * 1.25 * pt
    else:
        settings["letter_spacing"] = 0

style = {"fill": settings["offset_color"]}

if settings["offset_stroke"] is not None:
    offset_stroke_width = settings["offset_stroke_rate"] * settings["font_size"] * pt
    style["stroke"] = settings["offset_stroke"]
    style["stroke_width"] = offset_stroke_width

effect = path_effect('offset', attempt_force_join=False, is_visible=True, linejoin_type='miter',
                     miter_limit=2, offset=offset_size, unit='pt', update_on_knot_move=True)

filter = None
if settings["shadow_color"]:
    filter = create_shadow_filter(settings["shadow_color"], settings["shadow_opacity"],
                                  settings["shadow_blur_stddeviation"], settings["shadow_dx"], settings["shadow_dy"])

for item in items:
    if len(args.export_ids) > 0 and (item['no'] not in args.export_ids):
        continue

    text_group = create_text_group(item['lines'], base=[0, 0], font=settings["font_family"],
                                   font_size=(settings["font_size"] * pt), font_weight=settings["font_style"],
                                   fill=settings["text_color"], text_anchor=settings["text_anchor"], letter_spacing=settings["letter_spacing"])
    text_bb = None
    if settings["box_color"] or settings["shadow_color"]:
        text_bb = text_group.bounding_box()

    text_path = export_text_to_path(text_group, False)
    apply_path_effect(text_path, effect)
    text_path.style(**style)
    text_path.z_order('bottom')

    if filter is not None:
        text_path.style(filter=filter)
    #     g = group(text_group, text_path, filter=create_flood_filter(args.flood_bg_color))
    # else:
    #     g = group(text_group, text_path)
    target_list = [text_path, text_group]

    if settings["box_color"]:
        box_margin_x = settings["box_margin_x"] * settings["font_size"] * pt
        box_margin_y = settings["box_margin_y"] * settings["font_size"] * pt
        margin_offset_size = settings["offset_rate"] * settings["font_size"] * pt
        box = create_box(text_bb, settings["box_color"], opacity=settings["box_opacity"],
                         margin_x=box_margin_x + margin_offset_size, margin_y=box_margin_y + margin_offset_size)
        box.z_order('bottom')
        target_list.append(box)
    elif settings["shadow_color"]:
        box_margin_x = settings["box_margin_x"] * settings["font_size"] * pt
        box_margin_y = settings["box_margin_y"] * settings["font_size"] * pt
        margin_offset_size = settings["offset_rate"] * settings["font_size"] * pt
        shadow_offset_x = settings["shadow_dx"] * 2
        shadow_offset_y = settings["shadow_dy"] * 2
        box = create_box(text_bb, settings["box_color"], opacity=0,
                         margin_x=box_margin_x + margin_offset_size + shadow_offset_x,
                         margin_y=box_margin_y + margin_offset_size + shadow_offset_y)
        box.z_order('bottom')
        target_list.append(box)


    export_path = os.path.join(export_dir, f"{item['no']}.png")
    export_to_png(export_path)

    remove_objects(*target_list)
