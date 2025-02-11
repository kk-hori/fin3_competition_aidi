"""Markdownファイルのテキストをチャンク分割したTXTファイルを作成するスクリプト

Markdonw構造に最適な分割手法として LangChain の機能を使用する.
実行結果ファイルは以下の通り複数となる:
 - 無加工のチャンク結果(.json)
 - チャンク結果のコンテンツ部分(.md)
"""
import argparse
from pathlib import Path

from common.file_utils import dict_to_json, file_to_str, str_to_md_file
from common.load_config import get_input_dir, get_output_dir
from langchain.text_splitter import MarkdownHeaderTextSplitter

input_dir = get_input_dir()
output_dir = get_output_dir()


def parse_arguments() -> argparse.Namespace:
    """コマンドライン引数をパースする関数"""
    parser = argparse.ArgumentParser(
        description="指定した.mdのMarkdonw見出し構造に応じたチャンク分割結果ファイル群を作成する"
    )

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="チャンク分割対象の.mdファイル名を1個指定する"
    )

    return parser.parse_args()


def main():
    args = parse_arguments()
    file_name_input = args.input
    base_file_name = Path(file_name_input).stem
    path_input_file = input_dir / file_name_input
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "section_1"),
            ("##", "section_2"),
            ("###", "section_3"),
            ("####", "section_4"),
            ("#####", "section_5"),
        ]
    )
    md_content = file_to_str(path_input_file)
    documents = splitter.split_text(md_content)
    dict_chunk_result = {}
    for i, doc in enumerate(documents):
        path_output_md = output_dir / f"{base_file_name}_chunked_{i}.md"
        content = doc.page_content
        str_to_md_file(content, path_output_md)
        dict_chunk_result[i] = doc.to_json()
    path_output_json = output_dir / f"{base_file_name}_chunked.json"
    dict_to_json(dict_chunk_result, path_output_json)


if __name__ == "__main__":
    main()
