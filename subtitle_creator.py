# -*- coding: utf-8 -*-
import my_settings
import my_srt
from gimpfu import *
import os


def get_justyfy(name):
    if name == "left":
        return TEXT_JUSTIFY_LEFT
    elif name == "right":
        return TEXT_JUSTIFY_RIGHT
    elif name == "center":
        return TEXT_JUSTIFY_CENTER
    else:
        return TEXT_JUSTIFY_FILL


def to_str(utf_str):
    return utf_str.encode("ascii", "ignore")


def add_text(target_layer, text, hexColor, font_name, font_size, justify):
    image = pdb.gimp_item_get_image(target_layer)
    text_layer = pdb.gimp_text_fontname(
        image,
        target_layer,
        0,
        0,
        text,
        0,
        TRUE,
        font_size,
        PIXELS,
        font_name,
    )
    # 文字色を設定
    pdb.gimp_text_layer_set_color(text_layer, hexColor)
    # テキストをセンタリング
    pdb.gimp_text_layer_set_justification(text_layer, get_justyfy(justify))
    # offsetを初期化
    pdb.gimp_layer_set_offsets(text_layer, 0, 0)
    # 行間を調整
    # pdb.gimp_text_layer_set_line_spacing(text_layer, font_size * -0.25)
    return text_layer


def add_layer(image, name, color=None, opacity=100, idx=0):
    # 背景用のレイヤーを追加
    img_w = pdb.gimp_image_width(image)
    img_h = pdb.gimp_image_height(image)
    layer = pdb.gimp_layer_new(
        image, img_w, img_h, RGBA_IMAGE, name, opacity, LAYER_MODE_NORMAL_LEGACY
    )
    if color:
        org_color = pdb.gimp_context_get_background()
        pdb.gimp_context_set_background(color)
        pdb.gimp_drawable_fill(layer, FILL_BACKGROUND)
        pdb.gimp_context_set_background(org_color)
    else:
        pdb.gimp_drawable_fill(layer, TRANSPARENT_FILL)

    # レイヤーを画像に追加
    pdb.gimp_image_add_layer(image, layer, idx)
    return layer


def add_outline(image, target_layer, i, font_size, border_setting):
    outline_layer = pdb.gimp_layer_copy(target_layer, True)
    outline_layer.name = "アウトライン:{}".format(i)
    # ターゲットの下にレイヤーを配置
    pdb.gimp_image_add_layer(image, outline_layer, i + 1)
    # レイヤー内の画像のアウトラインを選択
    pdb.gimp_image_select_item(image, CHANNEL_OP_ADD, outline_layer)
    # 選択範囲を拡大
    pdb.gimp_selection_grow(image, font_size * border_setting["rate"])
    if border_setting["feather"] > 0:
        # 選択範囲の境界をぼかす
        pdb.gimp_selection_feather(image, font_size * border_setting["feather"])

    # 背景色を白に
    org_bg = pdb.gimp_context_get_background()
    pdb.gimp_context_set_background(to_str(border_setting["color"]))
    pdb.gimp_drawable_edit_fill(outline_layer, FILL_BACKGROUND)
    # 選択を解除
    pdb.gimp_selection_none(image)
    # 背景色を元にもどす
    pdb.gimp_context_set_background(org_bg)


def get_text_area(image, layer):
    # # 可視領域を選択
    pdb.gimp_image_select_item(image, CHANNEL_OP_ADD, layer)
    # 選択範囲が無い場合終了
    (non_empty, x1, y1, x2, y2) = pdb.gimp_selection_bounds(image)
    pdb.gimp_selection_none(image)
    if non_empty == 0:
        print("選択領域がない!!")
        return None
    else:
        return (x2 - x1, y2 - y1, x1, y1)


def generate_subtitles(subtitles, settings, output_dir, debug=False):
    for st in subtitles:
        print(st["no"])
        print("\n".join(st["lines"]))
        # imageの生成
        image = pdb.gimp_image_new(10, 10, RGB)
        tmp_layer = add_layer(image, "字幕")
        text_setting = settings["style"]["text"]
        # 字幕作成
        text_layer = add_text(
            tmp_layer,
            "\n".join(st["lines"]),
            to_str(text_setting["color"]),
            "Noto Sans JP Bold",
            48,
            to_str(text_setting["align"]),
        )

        font_size = text_setting["size"]
        canvas_setting = settings["canvas"]

        offset_x = font_size * canvas_setting["padding_x_rate"]
        offset_y = font_size * canvas_setting["padding_y_rate"]
        text_w = pdb.gimp_drawable_width(text_layer)
        text_h = pdb.gimp_drawable_height(text_layer)

        w = text_w + offset_x * 2
        h = text_h + offset_y * 2

        # テキストをレイヤーに貼り付け
        pdb.gimp_floating_sel_anchor(text_layer)
        # レイヤーのサイズ修正
        pdb.gimp_layer_resize(tmp_layer, w, h, offset_x, offset_y)
        pdb.gimp_image_resize(image, w, h, offset_x, offset_y)

        for i in range(settings["with_borders"]):
            border_setting = settings["style"]["borders"][i]
            if not border_setting:
                print("{}に該当するボーダー設定がありません".format(i))
                continue
            target_layer = image.layers[i]
            if not target_layer:
                print("{}に該当するレイヤーがありません".format(i))
                continue
            add_outline(image, target_layer, i, font_size, border_setting)

        if settings["with_shadow"]:
            shadow_setting = settings["style"]["shadow"]
            if shadow_setting:
                pdb.script_fu_drop_shadow(
                    image,
                    image.layers[-1],
                    shadow_setting["offset_x"],
                    shadow_setting["offset_y"],
                    shadow_setting["blur_radius"],
                    to_str(shadow_setting["color"]),
                    shadow_setting["blur_radius"] * 100,
                    False,
                )

        text_area = get_text_area(image, image.layers[0])

        if settings["with_box"]:
            box_setting = settings["style"]["box"]
            if box_setting:
                last_idx = len(image.layers)
                box_layer = add_layer(
                    image,
                    "BOX",
                    to_str(box_setting["color"]),
                    box_setting["opacity"] * 100,
                    last_idx,
                )
                pdx = box_setting["padding_x"]
                pdy = box_setting["padding_y"]
                ofx = text_area[2] - pdx
                ofy = text_area[3] - pdy
                pdb.gimp_layer_resize(
                    box_layer,
                    text_area[0] + pdx * 2,
                    text_area[1] + pdy * 2,
                    ofx * -1,
                    ofy * -1,
                )

        if not debug:
            # 可視レイヤーを1つに統合
            merged_layer = pdb.gimp_image_merge_visible_layers(image, CLIP_TO_IMAGE)
            merged_layer.name = "字幕 統合版"

            # crop
            crop_setting = settings["crop_area"]
            pdx = crop_setting["padding_x"]
            pdy = crop_setting["padding_y"]
            ofx = text_area[2] - pdx
            ofy = text_area[3] - pdy
            pdb.gimp_layer_resize(
                merged_layer,
                text_area[0] + pdx * 2,
                text_area[1] + pdy * 2,
                ofx * -1,
                ofy * -1,
            )
            pdb.gimp_image_resize(
                image,
                text_area[0] + pdx * 2,
                text_area[1] + pdy * 2,
                ofx * -1,
                ofy * -1,
            )
            # 画像出力
            output_path = os.path.join(output_dir, "{}.png".format(st["no"]))
            pdb.gimp_file_save(image, merged_layer, output_path, output_path)

        if debug:
            pdb.gimp_display_new(image)
        else:
            # imageの削除
            pdb.gimp_image_delete(image)


def run(srt_path, config_path, output_path, default_settings_path, debug=False):
    print("run!!: ", srt_path, config_path, output_path)
    default_config_path = os.path.abspath(default_settings_path)
    default_config = my_settings.read_config_file(default_config_path)
    print(default_config)
    abs_config_path = os.path.abspath(config_path)
    config = my_settings.read_config_file(abs_config_path)
    print(config)
    merged_config = my_settings.merge_settings(default_config, config)
    print(merged_config)
    abs_outpath = os.path.abspath(output_path)
    if not os.path.exists(abs_outpath):
        os.makedirs(abs_outpath)
    subtitles = my_srt.read_srt_file(os.path.abspath(srt_path))
    generate_subtitles(subtitles, merged_config, abs_outpath, debug)
    # gimp終了
    if not debug:
        pdb.gimp_quit(1)
