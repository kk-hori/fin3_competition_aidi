"""共通的なファイル操作の機能をまとめたモジュール

各スクリプトにおけるファイル操作時は，本モジュールに定義された機能を呼び出す.
"""
from pathlib import Path


def str_to_md_file(
        content: str,
        path_file_md: Path,
        encoding: str = "utf-8",
) -> None:
    """文字列をMarkdownファイルに書き出す関数

    指定したパスに.mdファイルを作成する.

    Args:
        content: .md書き出し対象の文字列
        path_file_md: 作成する.mdのパス
        encoding: 文字エンコード

    Returns:
        None
    """
    with open(path_file_md, "w", encoding=encoding) as f:
        f.write(content)
