# create-subtitle-image-by-gimp.py

GIMPを使って、字幕ファイル(SubRip形式)から字幕画像を生成します。

## 前提

このツールはDIY(大体で良いからやってみた)で作成しています。
今後、DIYでなく、ちゃんとしたツールにしてきたいと思っています。

以下の環境でのみ動作確認しています。

- macOS 13.1
- GIMP 2.10.36
- Python 2.7!! (GIMPに付属のPython)
- Python 3.10 (呼び出し用スクリプト用)

## インストール

本ツールは、[GIMP - GNU Image Manipulation Program](https://www.gimp.org/)とそのマクロである[Gimp Python](https://www.gimp.org/docs/python/)を利用しているので、**GIMP**を事前にインストールしてください。

あとは、本プロジェクトを適当なところにクローンしてください。

```shell
cd ~/work
git clone https://github.com/kantas-spike/create-subtitle-image-by-gimp.git
cd create-subtitle-image-by-gimp
```

`-h`オプションをつけて以下のシェルを実行し、ヘルプが表示されることを確認してください。

```shell
$ pwd
~/work/create-subtitle-image-by-gimp
$ sh ./create-subtitle-image-by-gimp.sh -h
usage: create-subtitle-image-by-gimp.py [-h] -s SRT_FILE -c CONFIG_PATH [-o OUTPUT_DIR] [--system-path SYSTEM_PATH] [--default-settings-path DEFAULT_SETTINGS_PATH] [--gimp-path GIMP_PATH]
                                        [--debug]

字幕ファイルから字幕画像を作成する

options:
  -h, --help            show this help message and exit
  -s SRT_FILE, --srt SRT_FILE
                        字幕ファイルパス
  -c CONFIG_PATH, --config CONFIG_PATH
                        設定ファイルパス
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        出力ディレクトリ(デフォルト: ./_images)
  --system-path SYSTEM_PATH
                        追加するシステムパス(デフォルト: .)
  --default-settings-path DEFAULT_SETTINGS_PATH
                        デフォルトの設定ファイルパス(デフォルト: ./default_settings.json)
  --gimp-path GIMP_PATH
                        GIMPの実行ファイルパス(デフォルト: gimp)
  --debug               デバッグモードで実行する
```

## 使い方

### コマンドラインオプションを利用する方法

以下のように、字幕ファイルのパスと、字幕画像を出力するディレクトリを指定します。

```sh
sh ./create-subtitle-image-by-gimp.sh -s 字幕ファイルのパス -c 設定ファイルのパス -o 画像出力先ディレクトリ
```

#### 例01

`sample_srt/sample.srt`に字幕ファイルのサンプルがあります。

```txt
1
00:00:02,000 --> 00:00:08,000
字幕ファイルから
字幕画像を生成します

2
00:00:10,000 --> 00:00:18,000
一重、二重の縁取り文字を作成できます

3
00:00:20,000 --> 00:00:28,000
影付きやボックスありの
字幕も作成できます
```

[sample_config/single_outline.json](./sample_config/single_outline.json)を使ってみましょう。

```json
{
  "with_shadow": false,
  "with_borders": 1,
  "with_box": false,
  "style": {
    "text": {
      "font_family": "Dela Gothic One",
      "size": 48,
      "color": "#c4c837",
      "align": "center",
      "line_space_rate": -0.3
    },
    "borders": [{ "color": "#377ac8", "rate": 0.08, "feather": 0 }]
  }
}
```

この字幕ファイルから字幕画像を生成するには、以下を実行します。

```sh
$ sh ./create-subtitle-image-by-gimp.sh -s ./sample_srt/sample.srt -c ./sample_config/single_outline.json -o sample_output/01
```

- 実行結果

  | 字幕No | 画像                             |
  | ------ | -------------------------------- |
  | 1.png  | ![1.png](sample_output/01/1.png) |
  | 2.png  | ![2.png](sample_output/01/2.png) |
  | 3.png  | ![3.png](sample_output/01/3.png) |

#### 例02

[sample_config/dobule_outline_with_box.json](./sample_config/dobule_outline_with_box.json)を使ってみましょう。

```json
{
  "with_shadow": false,
  "with_borders": 2,
  "with_box": true,
  "style": {
    "text": {
      "font_family": "Noto Sans JP Bold",
      "size": 48,
      "color": "#f3ffed",
      "align": "center",
      "line_space_rate": -0.3
    },
    "borders": [
      { "color": "#0f491e", "rate": 0.08, "feather": 0 },
      { "color": "#f0e2c5", "rate": 0.08, "feather": 0 }
    ],
    "box": {
      "color": "#888888"
    }
  }
}
```

```sh
$ sh ./create-subtitle-image-by-gimp.sh -s ./sample_srt/sample.srt -c ./sample_config/dobule_outline_with_box.json -o sample_output/02
```

- 実行結果

  | 字幕No | 画像                             |
  | ------ | -------------------------------- |
  | 1.png  | ![1.png](sample_output/02/1.png) |
  | 2.png  | ![2.png](sample_output/02/2.png) |
  | 3.png  | ![3.png](sample_output/02/3.png) |

  #### 例03

[sample_config/dobule_outline_with_box_shadow.json](./sample_config/dobule_outline_with_box_shadow.json)を使ってみましょう。

```json
{
  "with_shadow": true,
  "with_borders": 2,
  "with_box": true,
  "style": {
    "text": {
      "font_family": "Noto Sans JP Bold",
      "size": 48,
      "color": "#f3ffed",
      "align": "center",
      "line_space_rate": -0.3
    },
    "borders": [
      { "color": "#0f491e", "rate": 0.08, "feather": 0 },
      { "color": "#f0e2c5", "rate": 0.08, "feather": 0 }
    ],
    "box": {
      "color": "#888888"
    },
    "shadow": {
      "offset_x": 5,
      "offset_y": 5,
      "blur_radius": 15
    }
  }
}
```

```sh
$ sh ./create-subtitle-image-by-gimp.sh -s ./sample_srt/sample.srt -c ./sample_config/dobule_outline_with_box_shadow.json -o sample_output/03
```

- 実行結果

  | 字幕No | 画像                             |
  | ------ | -------------------------------- |
  | 1.png  | ![1.png](sample_output/03/1.png) |
  | 2.png  | ![2.png](sample_output/03/2.png) |
  | 3.png  | ![3.png](sample_output/03/3.png) |

## 設定

設定ファイルには以下の項目を指定できます。
設定ファイルで未指定の項目はデフォルト値が採用されます。

| 設定項目       | デフォルト値 | 説明                                                          |
| -------------- | ------------ | ------------------------------------------------------------- |
| "with_shadow"  | false        | 影付きの字幕画像を作成する                                    |
| "with_borders" | 2            | 縁取り数を指定する。0の場合は縁取らない。最大2まで指定可能    |
| "with_box"     | false        | 字幕画像に背景色をつける                                      |
| "crop_area"    | 別掲         | 字幕画像のパディング設定                                      |
| "canvas"       | 別掲         | 内部で使用するキャンバスのパディング設定 (通常変更の必要なし) |
| "style"        | 別掲         | 文字、縁取り、影付け、背景色のスタイル設定                    |

### crop_area(字幕画像のパディング)設定

| crop_area内設定項目 | デフォルト値 | 説明                                     |
| ------------------- | ------------ | ---------------------------------------- |
| "padding_x"         | 20           | 字幕画像の水平パディングサイズ(単位: px) |
| "padding_y"         | 20           | 字幕画像の垂直パディングサイズ(単位: px) |

### canvas(キャンバスのパディング)設定

| canvas内設定項目 | デフォルト値 | 説明                                                     |
| ---------------- | ------------ | -------------------------------------------------------- |
| "padding_x_rate" | 1.0          | キャンバスの水平パディングサイズ(単位: 文字サイズの比率) |
| "padding_y_rate" | 1.0          | キャンバスの垂直パディングサイズ(単位: 文字サイズの比率) |

"padding_x_rate"に`2.0`指定すると、字幕画像を描画しているキャンバスに2文字分の余白が設定される。

### style設定

| style内設定項目 | デフォルト値 | 説明             |
| --------------- | ------------ | ---------------- |
| "text"          | 別掲         | 文字のスタイル   |
| "borders"       | 別掲         | 縁取りのスタイル |
| "shadow"        | 別掲         | 影のスタイル     |
| "box"           | 別掲         | 背景色のスタイル |

#### text設定

| text内設定項目    | デフォルト値        | 説明                             |
| ----------------- | ------------------- | -------------------------------- |
| "font_family"     | "Noto Sans JP Bold" | フォントファミリー               |
| "size"            | 48                  | フォントサイズ (単位: px)        |
| "color"           | "#40516a"           | 文字の前景色                     |
| "justification"   | "center"            | 文字揃え(left,right,center,fill) |
| "line_space_rate" | -0.3                | 行間 (単位:文字サイズの比率)     |

#### borders設定

最大2個分の縁取り設定を持つ配列。
配列のインデックスの小さい方が内側の縁取りとなる。

| no  | borders内設定項目 | デフォルト値 | 説明                                                    |
| --- | ----------------- | ------------ | ------------------------------------------------------- |
| 1   | "color"           | "#FFFFFF"    | 縁取りの色                                              |
|     | "rate"            | 0.08         | 縁取りのサイズ(単位:文字サイズの比率)                   |
|     | "feather"         | 0            | 縁取りをぼかし幅(単位: px)。0の場合、縁取りをぼかさない |
| 2   | "color"           | "#40516a"    | 縁取りの色                                              |
|     | "rate"            | 0.08         | 縁取りのサイズ(単位:文字サイズの比率)                   |
|     | "feather"         | 0            | 縁取りをぼかし幅(単位: px)。0の場合、縁取りをぼかさない |

"rate"に`0.08`指定すると、幅が`文字サイズ * 0.08`の縁取りが作成される。

#### shadoe設定

| shadow内設定項目 | デフォルト値 | 説明                          |
| ---------------- | ------------ | ----------------------------- |
| "color"          | "#000000"    | 影の色                        |
| "offset_x"       | 10           | 影の水平オフセット (単位: px) |
| "offset_y"       | 10           | 影の垂直オフセット (単位: px) |
| "blur_radius"    | "center"     | 影のぼかし半径 (単位: px)     |
| "opacity"        | 0.5          | 影の色の不透明度 (0〜1.0)     |

#### box設定

| box内設定項目 | デフォルト値 | 説明                                     |
| ------------- | ------------ | ---------------------------------------- |
| "padding_x"   | 20           | 字幕画像の水平パディングサイズ(単位: px) |
| "padding_y"   | 20           | 字幕画像の垂直パディングサイズ(単位: px) |
| "color"       | "#cccccc"    | 字幕の背景色                             |
| "opacity"     | 1.0          | 背景色の不透明度 (0〜1.0)                |

### [デフォルト設定ファイル](./default_settings.json)は以下になります。

```json
{
  "with_shadow": true,
  "with_borders": 2,
  "with_box": true,
  "crop_area": { "padding_x": 20, "padding_y": 20 },
  "canvas": { "padding_x_rate": 1.0, "padding_y_rate": 1.0 },
  "style": {
    "text": {
      "font_family": "Noto Sans JP Bold",
      "size": 48,
      "color": "#40516a",
      "justification": "center"
    },
    "borders": [
      { "color": "#FFFFFF", "rate": 0.08, "feather": 0 },
      { "color": "#40516a", "rate": 0.08, "feather": 0 }
    ],
    "shadow": {
      "color": "#000000",
      "offset_x": 10,
      "offset_y": 10,
      "blur_radius": 15,
      "opacity": 0.5
    },
    "box": {
      "padding_x": 20,
      "padding_y": 20,
      "color": "#cccccc",
      "opacity": 1.0
    }
  }
}
```

コマンドラインで指定した設定ファイルは、デフォルト設定を上書きします。

## 参考

- [GIMP - GNU Image Manipulation Program](https://www.gimp.org/)
- [GIMP - Automate Editing](https://www.gimp.org/tutorials/Automate_Editing_in_GIMP/)
- [Gimp Python Documentation](https://www.gimp.org/docs/python/)
