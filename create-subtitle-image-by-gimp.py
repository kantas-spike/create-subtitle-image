import argparse
import subprocess


def create_command_line(
    additional_sys_path, srt_path, config_path, output_dir, gimp_path="gimp"
):
    cmd = (
        f"{gimp_path} -idsc --batch-interpreter python-fu-eval "
        f'--batch "import sys;sys.path=[{repr(additional_sys_path)}]+sys.path;'
        "import subtitle_creator;"
        f'subtitle_creator.run({repr(srt_path)}, {repr(config_path)}, {repr(output_dir)})"'
    )
    return cmd


def run_gimp(cmd):
    subprocess.run(cmd, shell=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "create-subtitle-image-by-gimp.py", description="字幕ファイルから字幕画像を作成する"
    )
    parser.add_argument(
        "-s", "--srt", required=True, help="字幕ファイルパス", metavar="SRT_FILE"
    )
    parser.add_argument(
        "-c", "--config", required=True, help="設定ファイルパス", metavar="CONFIG_PATH"
    )

    DEFAULT_OUTPUT_DIR = "./_images"
    parser.add_argument(
        "-o",
        "--output-dir",
        required=False,
        help=f"出力ディレクトリ(デフォルト: {DEFAULT_OUTPUT_DIR})",
        metavar="OUTPUT_DIR",
        default=DEFAULT_OUTPUT_DIR,
    )

    DEFAULT_SYSTEM_PATH = "."
    parser.add_argument(
        "--system-path",
        required=False,
        help=f"追加するシステムパス(デフォルト: {DEFAULT_SYSTEM_PATH})",
        metavar="SYSTEM_PATH",
        default=DEFAULT_SYSTEM_PATH,
    )
    DEFAULT_GIMP_PATH = "gimp"
    parser.add_argument(
        "--gimp-path",
        required=False,
        help=f"GIMPの実行ファイルパス(デフォルト: {DEFAULT_GIMP_PATH})",
        metavar="GIMP_PATH",
        default=DEFAULT_GIMP_PATH,
    )
    args = parser.parse_args()
    print(args)
    cmdline = create_command_line(
        args.system_path, args.srt, args.config, args.output_dir
    )
    print("cmdline:", cmdline)
    run_gimp(cmdline)
