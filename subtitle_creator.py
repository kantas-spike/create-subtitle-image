# -*- coding: utf-8 -*-
import my_settings
import my_srt
from gimpfu import *
import os


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
    pdb.gimp_text_layer_set_justification(text_layer, justify)
    # offsetを初期化
    pdb.gimp_layer_set_offsets(text_layer, 0, 0)
    # 行間を調整
    # pdb.gimp_text_layer_set_line_spacing(text_layer, font_size * -0.25)
    return text_layer


def add_layer(image, color=None, idx=0):
    # 背景用のレイヤーを追加
    img_w = pdb.gimp_image_width(image)
    img_h = pdb.gimp_image_height(image)
    layer = pdb.gimp_layer_new(
        image, img_w, img_h, RGBA_IMAGE, "背景", 100, LAYER_MODE_NORMAL_LEGACY
    )
    if color:
        org_color = pdb.gimp_context_get_background()
        pdb.gimp_context_set_background(color)
        pdb.gimp_drawable_fill(layer, FILL_BACKGROUND)
        pdb.gimp_context_set_background(org_color)
    else:
        pdb.gimp_drawable_fill(layer, TRANSPARENT_FILL)

    # レイヤーを画像の先頭に追加
    pdb.gimp_image_add_layer(image, layer, idx)
    return layer


def generate_subtitles(subtitles, settings, output_dir):
    for st in subtitles:
        print(st["no"])
        print("\n".join(st["lines"]))
        # imageの生成
        image = pdb.gimp_image_new(10, 10, RGB)
        tmp_layer = add_layer(image)
        # 字幕作成
        text_layer = add_text(
            tmp_layer,
            "\n".join(st["lines"]),
            "#40516a",
            "Noto Sans JP Bold",
            48,
            TEXT_JUSTIFY_CENTER,
        )

        w = pdb.gimp_drawable_width(text_layer)
        h = pdb.gimp_drawable_height(text_layer)

        # テキストをレイヤーに貼り付け
        pdb.gimp_floating_sel_anchor(text_layer)

        pdb.gimp_layer_resize(tmp_layer, w, h, 0, 0)
        pdb.gimp_image_resize(image, w, h, 0, 0)

        # 可視領域を選択
        pdb.gimp_image_select_item(image, CHANNEL_OP_ADD, tmp_layer)
        # 選択範囲が無い場合終了
        (non_empty, x1, y1, x2, y2) = pdb.gimp_selection_bounds(image)
        if non_empty == 0:
            print("選択領域がないため無視!!")
        else:
            offset_x, offset_y = pdb.gimp_drawable_offsets(tmp_layer)
            new_w = x2 - x1
            new_h = y2 - y1
            pdb.gimp_image_resize(image, new_w, new_h, x1 * -1, y1 * -1)
            # 画像出力
            output_path = os.path.join(output_dir, "{}.png".format(st["no"]))
            # 可視レイヤーを1つに統合
            merged_layer = pdb.gimp_image_merge_visible_layers(image, CLIP_TO_IMAGE)
            pdb.gimp_file_save(image, merged_layer, output_path, output_path)

        # imageの削除
        # pdb.gimp_display_new(image)
        pdb.gimp_image_delete(image)


def run(srt_path, config_path, output_path):
    print("run!!: ", srt_path, config_path, output_path)
    abs_config_path = os.path.abspath(config_path)
    config = my_settings.read_config_file(abs_config_path)
    print(config)
    abs_outpath = os.path.abspath(output_path)

    if not os.path.exists(abs_outpath):
        os.makedirs(abs_outpath)
    subtitles = my_srt.read_srt_file(os.path.abspath(srt_path))
    generate_subtitles(subtitles, config, abs_outpath)
    # gimp終了
    pdb.gimp_quit(1)
