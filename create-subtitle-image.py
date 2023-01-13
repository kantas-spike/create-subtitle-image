import inkex
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


DEFAULT_FONT_SIZE = 48
DEFAULT_LINE_SEP = 1.1
DEFAULT_FONT_FAMILY = "BIZ UDGothic"
DEFAULT_FONT_WEIGHT = "normal"
DEFAULT_TEXT_ANCHOR = "middle"
COLOR_WHITE = "#000000"
COLOR_BLACK = "#FFFFFF"
DEFAULT_OFFSET_RATE = 0.06
DEFAULT_OFFSET_STROKE_RATE = 0.03
DEFAULT_BASE_DIR = os.path.expanduser("~")
DEFAULT_EXPORT_DIR = "~/tmp/create-subtitle-image"

parser = argparse.ArgumentParser(prog="create-subtitle-image")
parser.add_argument("--font-size", type=float, default=DEFAULT_FONT_SIZE,
                    help=f"字幕テキストのフォントサイズ(単位:pt). (デフォルト値: {DEFAULT_FONT_SIZE})")
parser.add_argument("--line-sep", type=float, default=DEFAULT_LINE_SEP,
                    help=f"字幕テキストの行間. (デフォルト値: {DEFAULT_LINE_SEP})")
parser.add_argument("--font-family", type=str, default=DEFAULT_FONT_FAMILY,
                    help=f"字幕テキストのフォントファミリー. (デフォルト値: {DEFAULT_FONT_FAMILY})")
parser.add_argument("--font-weight", choices=("normal", "bold", "lighter", "bolder", "100", "200", "300", "400", "500",
                    "600", "700", "800", "900"), type=str, default=DEFAULT_FONT_WEIGHT,
                    help=f"字幕テキストのフォントの太さ. (デフォルト値: {DEFAULT_FONT_WEIGHT})")
parser.add_argument("--text-anchor", choices=("start", "middle", "end"),
                    type=str, default=DEFAULT_TEXT_ANCHOR, help=f"テキストのアンカー. (デフォルト値: {DEFAULT_TEXT_ANCHOR})")
parser.add_argument("--text-color", type=str,
                    default=COLOR_BLACK, help=f"テキストの色. (デフォルト値: {COLOR_BLACK})")
parser.add_argument("--offset-rate", type=float,
                    default=DEFAULT_OFFSET_RATE, help=f"縁取り用に拡大する割合.基準はフォントサイズ. (デフォルト値: {DEFAULT_OFFSET_RATE})")
parser.add_argument("--offset-color", type=str,
                    default=COLOR_WHITE, help=f"縁取りの色. (デフォルト値: {COLOR_WHITE})")
parser.add_argument("--offset-stroke", type=str, default=None,
                    help="縁取りの枠線の色.色未指定の場合は枠線を表示しない. (デフォルト値: なし)")
parser.add_argument("--offset-stroke-rate", type=float, default=DEFAULT_OFFSET_STROKE_RATE,
                    help=f"縁取りの枠線の幅.基準はフォントサイズ. (デフォルト値: {DEFAULT_OFFSET_STROKE_RATE})")

parser.add_argument("--srt-path", type=str, help="字幕ファイルのパス")
parser.add_argument("--export-dir", type=str,
                    default=DEFAULT_EXPORT_DIR, help=f"作成した字幕画像の出力先dir. (デフォルト値: {DEFAULT_EXPORT_DIR})")
parser.add_argument("--base-dir", type=str, default=DEFAULT_BASE_DIR,
                    help=f"相対パスを絶対パスに変換する際に基準とするディレクトリ. (デフォルト値: {DEFAULT_BASE_DIR})")

args = parser.parse_args(rest_args)

srt_path = expand_path(args.srt_path, args.base_dir)
export_dir = expand_path(args.export_dir, args.base_dir)
# print(args, srt_path, export_dir)
if not os.path.isdir(export_dir):
    os.makedirs(export_dir)

items = read_srt_file(srt_path)
offset_size = args.offset_rate * args.font_size
style = {"fill": args.offset_color}

if args.offset_stroke is not None:
    offset_stroke_width = args.offset_stroke_rate * args.font_size * pt
    style["stroke"] = args.offset_stroke
    style["stroke_width"] = offset_stroke_width

effect = path_effect('offset', attempt_force_join=False, is_visible=True, linejoin_type='miter',
                     miter_limit=2, offset=offset_size, unit='pt', update_on_knot_move=True)

for item in items:
    g = create_text_group(item['lines'], base=[0, 0], font=args.font_family, font_size=(args.font_size * pt),
                          font_weight=args.font_weight, fill=args.text_color, text_anchor=args.text_anchor)
    text_path = export_text_to_path(g, False)
    apply_path_effect(text_path, effect)
    # print(style)
    text_path.style(**style)
    text_path.z_order('bottom')
    export_path = os.path.join(export_dir, f"{item['no']}.png")
    export_to_png(export_path)
    remove_objects(text_path, g)
