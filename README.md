# create-subtitle-image

字幕ファイル(SubRip形式)から字幕画像を生成します。

## 前提

このツールはDIY(大体で良いからやってみた)で作成しています。
今後、DIYでなく、ちゃんとしたツールにしてきたいと思っています。

以下の環境でのみ動作確認しています。

- macOS 13.1
- Inkscape 1.2.2
- Simple Inkscape Scripting (c62fa9e のコミット以降)
- Python 3.10.7 (Inkscapeに付属のPython)


## インストール

本ツールは、[Inkscape](https://inkscape.org/)とその拡張機能である[Simple Inkscape Scripting](https://github.com/spakin/SimpInkScr)を利用しているので、事前にインストールしてください。

あとは、本プロジェクトを適当なところにクローンしてください。

~~~shell
cd ~/work
git clone https://github.com/kantas-spike/create-subtitle-image.git
cd create-subtitle-image
~~~

`-h`オプションをつけて以下のシェルを実行し、ヘルプが表示されることを確認してください。

~~~shell
$ pwd
~/work/create-subtitle-image
$ sh ./create-subtitle-image.sh
usage: create-subtitle-image [-h] [--font-size FONT_SIZE] [--font-family FONT_FAMILY] [--font-style FONT_STYLE] [--text-anchor {start,middle,end}] [--line-sep LINE_SEP] [--text-color TEXT_COLOR] [--letter-spacing LETTER_SPACING] [--offset-rate OFFSET_RATE]
                             [--offset-color OFFSET_COLOR] [--offset-stroke OFFSET_STROKE] [--offset-stroke-rate OFFSET_STROKE_RATE] [--shadow-color SHADOW_COLOR] [--box-color BOX_COLOR] --srt-path SRT_PATH [--config-path CONFIG_PATH] --export-dir EXPORT_DIR
                             [--base-dir BASE_DIR]

options:
  -h, --help            show this help message and exit
  --font-size FONT_SIZE
                        字幕テキストのフォントサイズ(単位:pt). (デフォルト値: 48)
  --font-family FONT_FAMILY
                        字幕テキストのフォントファミリー. (デフォルト値: BIZ UDGothic)
  --font-style FONT_STYLE
                        字幕テキストのフォントのスタイル. (デフォルト値: normal)
  --text-anchor {start,middle,end}
                        テキストのアンカー. (デフォルト値: middle)
  --line-sep LINE_SEP   字幕テキストの行間. (デフォルト値: 1.1)
  --text-color TEXT_COLOR
                        テキストの色. (デフォルト値: #FFFFFF)
  --letter-spacing LETTER_SPACING
                        文字の間隔. (デフォルト値: なし)
  --offset-rate OFFSET_RATE
                        縁取り用に拡大する割合.基準はフォントサイズ. (デフォルト値: 0.06)
  --offset-color OFFSET_COLOR
                        縁取りの色. (デフォルト値: #000000)
  --offset-stroke OFFSET_STROKE
                        縁取りの枠線の色.色未指定の場合は枠線を表示しない. (デフォルト値: なし)
  --offset-stroke-rate OFFSET_STROKE_RATE
                        縁取りの枠線の幅.基準はフォントサイズ. (デフォルト値: 0.03)
  --shadow-color SHADOW_COLOR
                        影の色.色未指定の場合は影を表示しない. (デフォルト値: なし)
  --box-color BOX_COLOR
                        背景色.色未指定の場合は背景を塗り潰さない. (デフォルト値: なし)
  --srt-path SRT_PATH   字幕ファイルのパス
  --config-path CONFIG_PATH
                        設定ファイル(json形式)のパス
  --export-dir EXPORT_DIR
                        作成した字幕画像の出力先dir.
  --base-dir BASE_DIR   相対パスを絶対パスに変換する際に基準とするディレクトリ. (デフォルト値: /Users/kanta)
~~~

もし、エラーが表示される場合は、`create-subtitle-image.sh`の環境変数の定義を環境にあわせて修正してください。

## 使い方

### コマンドラインオプションを利用する方法

以下のように、字幕ファイルのパスと、字幕画像を出力するディレクトリを指定します。

~~~sh
sh ./create-subtitle-image.sh --srt-path 字幕ファイルのパス --export-dir 画像出力先ディレクトリ
~~~

#### 例01

`sample_srt/sample.srt`に字幕ファイルのサンプルがあります。

~~~txt
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
~~~

この字幕ファイルから字幕画像を生成するには、以下を実行します。(デフォルトのフォントサイズは48ptと大きいので、例では24ptに設定しています。)

~~~sh
$ sh ./create-subtitle-image.sh --srt-path ./sample_srt/sample.srt --export-dir sample_output/01 --font-size 24
~~~

- 実行結果

    字幕ファイルに記載された番号で画像が生成されます。
    デフォルトでは白文字黒縁取りです。

    | 字幕No | 画像 |
    | ------ | ---- |
    | 1.png | ![1.png](sample_output/01/1.png) |
    | 2.png | ![2.png](sample_output/01/2.png) |
    | 3.png | ![3.png](sample_output/01/3.png) |

#### 例02

フォントスタイルをBold, 文字色を赤、縁取り色を青にしてみましょう。

~~~sh
$ sh ./create-subtitle-image.sh --srt-path ./sample_srt/sample.srt --export-dir sample_output/02 --text-color "#c84137" --offset-color "#6193d1" --font-size 24 --font-style bold
~~~

- 実行結果

    | 字幕No | 画像 |
    | ------ | ---- |
    | 1.png | ![1.png](sample_output/02/1.png)|
    | 2.png | ![2.png](sample_output/02/2.png)|
    | 3.png | ![3.png](sample_output/02/3.png)|


#### 例03

今度は、フォントに[Dela Gothic One](https://fonts.google.com/specimen/Dela+Gothic+One?subset=japanese&noto.script=Jpan)を使ってみましょう。(フォントは事前にインストールして下さい)

~~~sh
$ sh ./create-subtitle-image.sh --srt-path ./sample_srt/sample.srt --export-dir sample_output/03 --font-family "Dela Gothic One" --text-color "#c4c837" --offset-color "#377ac8" --font-size 24
~~~

- 実行結果

    | 字幕No | 画像 |
    | ------ | ---- |
    | 1.png | ![1.png](sample_output/03/1.png)|
    | 2.png | ![2.png](sample_output/03/2.png)|
    | 3.png | ![3.png](sample_output/03/3.png)|

### 設定ファイルを利用する方法

JSONファイルにまとめて設定できます。

~~~json
{
    "font_size": 24,
    "font_style": "bold",
    "text_color": "#f3ffed",
    "offset_color": "#0f491e",
    "offset_stroke": "#f0e2c5",
    "offset_rate": 0.08
}
~~~

以下のように、字幕ファイルのパスと、字幕画像を出力するディレクトリに加え、設定ファイルのパスを指定すれば利用できます。

~~~sh
sh ./create-subtitle-image.sh --srt-path 字幕ファイルのパス --export-dir 画像出力先ディレクトリ --config-path JSONファイルのパス
~~~

#### 例04

`sample_config/green_with_box.json`を使ってみましょう。

```json
{
    "font_size": 24,
    "font_style": "bold",
    "text_color": "#f3ffed",
    "offset_color": "#0f491e",
    "offset_stroke": "#f0e2c5",
    "offset_rate": 0.08,
    "box_color": "#888888"
}
```

~~~sh
$ sh ./create-subtitle-image.sh --srt-path ./sample_srt/sample.srt --export-dir sample_output/04 --config-path ./sample_config/green_with_box.json
~~~

- 実行結果

  二重縁取りのボックス付き字幕が表示されました。

    | 字幕No | 画像 |
    | ------ | ---- |
    | 1.png | ![1.png](sample_output/04/1.png)|
    | 2.png | ![2.png](sample_output/04/2.png)|
    | 3.png | ![3.png](sample_output/04/3.png)|

#### 例05

`sample_config/green_with_shadow.json`を使ってみましょう。

```json
{
    "font_size": 24,
    "font_style": "bold",
    "text_color": "#f3ffed",
    "offset_color": "#0f491e",
    "offset_stroke": "#f0e2c5",
    "offset_rate": 0.08,
    "shadow_color": "#EEEEEE"
}
```

~~~sh
$ sh ./create-subtitle-image.sh --srt-path ./sample_srt/sample.srt --export-dir sample_output/05 --config-path ./sample_config/green_with_shadow.json
~~~

- 実行結果

  二重縁取りの影付き字幕が表示されました。

    | 字幕No | 画像 |
    | ------ | ---- |
    | 1.png | ![1.png](sample_output/05/1.png)|
    | 2.png | ![2.png](sample_output/05/2.png)|
    | 3.png | ![3.png](sample_output/05/3.png)|

## 設定

設定ファイルには以下の項目を指定できます。

| 設定項目 | デフォルト値 | 説明 |
| -------- | ------------ | ---- |
| "font_size" | 48 | 字幕テキストのフォントサイズ(単位:pt) |
| "font_family" | "BIZ UDGothic" | 字幕テキストのフォントファミリー(事前に該当フォントをインストールする必要あり) |
| "font_style" | "normal" | 字幕テキストのフォントのスタイル |
| "text_anchor" | "middle" | テキストの配置方法(start: 左揃え, middle: 中央揃え, end: 右揃え) |
| "text_color" | "#000000" | テキストの色 |
| "line_sep" | 1.1 | 字幕テキストの行間 |
| "letter_spacing" | なし | 文字の間隔 |
| "offset_rate" | 0.06 | 縁取り用に拡大する割合.基準はフォントサイズ |
| "offset_color" | "#FFFFFF" | 縁取りの色 |
| "offset_stroke_rate" | 0.03 | 縁取りの枠線の幅.基準はフォントサイズ |
| "offset_stroke" | なし | 縁取りの枠線の色.色未指定の場合は枠線を表示しない |
| "box_margin_x" | 0.5 | ボックスの左右のそれぞれのマージン.基準はフォントサイズ |
| "box_margin_y" | 0.25 | ボックスの上下のそれぞれのマージン.基準はフォントサイズ |
| "box_opacity" | 0.3 | ボックス色の不透明度 |
| "box_color" | なし | ボックスの色. 色未指定の場合はボックスを表示しない |
| "shadow_opacity" | 0.3 | 影の色の不透明度 |
| "shadow_blur_stddeviation" | 1.5 | 影のぼかしの標準偏差 |
| "shadow_dx" | 1.5 | 影の横方向の表示位置.(単位:px) |
| "shadow_dy" | 1.5 | 影の縦方向の表示位置.(単位:px) |
| "shadow_color" | なし | 影の色. 色未指定の場合は影を表示しない |
