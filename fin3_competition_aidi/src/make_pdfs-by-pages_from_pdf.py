"""PDFをページ分割したPDFを作成するスクリプト

スクリプト実行時のコマンドライン引数でページ分割対象のPDFを指定する.
"""
import argparse
from pathlib import Path

from common.load_config import get_input_dir, get_output_dir
from pypdf import PdfReader, PdfWriter

input_dir = get_input_dir()
output_dir = get_output_dir()


def parse_arguments() -> argparse.Namespace:
    """コマンドライン引数をパースする関数"""
    parser = argparse.ArgumentParser(
        description="指定した.pdfをページ分割した.pdfを作成する"
    )

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="ページ分割対象の.pdfファイル名を1個指定する"
    )

    return parser.parse_args()


def main():
    args = parse_arguments()
    file_name_input = args.input
    base_file_name = Path(file_name_input).stem
    path_input_file = input_dir / file_name_input
    reader = PdfReader(path_input_file)
    for index in range(len(reader.pages)):
        writer = PdfWriter()
        pdf = reader.pages[index]
        writer.add_page(pdf)
        path_output_file = output_dir / f"{base_file_name}_{index}.pdf"
        with open(path_output_file, "wb") as f:
            writer.write(f)


if __name__ == "__main__":
    main()
