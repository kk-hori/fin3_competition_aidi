"""Markdownファイルのテキストをチャンク分割したTXTファイルを作成するスクリプト

Markdonw構造に最適な分割手法として LangChain の機能を使用する.
実行結果ファイルは以下の通り複数となる:
 - チャンク結果のメタデータおよびコンテンツ(.json)
 - チャンク結果のコンテンツ(.md)
"""
import argparse
from pathlib import Path

from common.file_utils import dict_to_json, file_to_str, str_to_md_file
from common.load_config import get_input_dir, get_output_dir, load_config
from common.string_utils import count_tokens
from langchain.schema import Document
from langchain.text_splitter import (MarkdownHeaderTextSplitter,
                                     RecursiveCharacterTextSplitter)

config = load_config()
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


def split_markdown(
        md_text: str,
) -> list[Document]:
    """Markdownテキストを階層構造に応じて分割する関数

    分割粒度は関数内で固定されていることに注意する.

    Args:
        md_text: Markdown構造の文字列

    Returns:
        分割結果
    """
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "section_1"),
            ("##", "section_2"),
            ("###", "section_3"),
            ("####", "section_4"),
            ("#####", "section_5"),
        ]
    )
    return splitter.split_text(md_text)


def split_recursive_character(
        text: str,
        chunk_size: int = 3000,
        chunk_overlap: int = 500,
        separators: list[str] = ["\n\n", "\n", "。", "、", " "]
) -> list[str]:
    """テキストを再起的に分割する関数

    分割ルールを引数で指定する.

    Args:
        text: 分割対象の文字列
        chunk_size: 1チャンクの最大文字数
        chunk_overlap: オーバラップサイズ
        separators: 優先度の高い分割ポイント

    Returns:
        分割結果
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
    )
    return splitter.split_text(text)


def main():
    args = parse_arguments()
    file_name_input = args.input
    base_file_name = Path(file_name_input).stem
    path_input_file = input_dir / file_name_input
    md_content = file_to_str(path_input_file)
    documents = split_markdown(md_content)
    dict_chunk_result = {}
    model_name = config["azure_openai"]["embedding"]["model_name"]
    max_tokens = config["azure_openai"]["embedding"]["max_tokens"]
    additonal_id = 0  # 全体のチャンクID加算用
    chunk_total = 0
    for i, doc in enumerate(documents):
        metadata = doc.metadata
        content = doc.page_content
        content_tokens = count_tokens(content, model_name)
        if content_tokens <= max_tokens:
            id = i + additonal_id
            path_output_md = output_dir / f"{base_file_name}_chunked_{id}.md"
            str_to_md_file(content, path_output_md)
            item = {
                "metadata": metadata,
                "content": content,
            }
            dict_chunk_result[id] = item
            chunk_total += 1
        else:
            sub_contents = split_recursive_character(content)
            sub_length = len(sub_contents)
            for j, sub_content in enumerate(sub_contents):
                id = i + additonal_id + j
                path_output_md = output_dir / \
                    f"{base_file_name}_chunked_{id}.md"
                str_to_md_file(sub_content, path_output_md)
                item = {
                    "metadata": metadata,
                    "content": sub_content,
                }
                dict_chunk_result[id] = item
                chunk_total += 1
            additonal_id += sub_length - 1
    path_output_json = output_dir / f"{base_file_name}_chunked.json"
    dict_to_json(dict_chunk_result, path_output_json)
    print(f"total chunks: {chunk_total}")


if __name__ == "__main__":
    main()
