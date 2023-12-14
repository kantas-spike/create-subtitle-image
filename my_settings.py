# -*- coding: utf-8 -*-

DEFAULT_SETTINGS = {
    "type": "normal",
    "with_shadow": False,
    "with_borders": 0,
    "with_box": False,
    "style": {
        "text": {
            "font_family": "Noto Sans JP Bold",
            "size": 48,
            "color": "#40516a",
            "align": "center",
            "feather": 0,
        },
        "first_border": {"color": "#000000", "rate": 0.1, "feather": 0},
        "second_border": {"color": "#000000", "rate": 0.1, "feather": 0},
        "shadow": {"color": "#000000", "size": 1},
    },
}


def read_config_file(path):
    return DEFAULT_SETTINGS
