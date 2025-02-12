"""共通的なファイル操作の機能をまとめたモジュール

各スクリプトにおけるファイル操作時は，本モジュールに定義された機能を呼び出す.
"""
import csv
import json
from pathlib import Path

from typing_extensions import Any


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


def file_to_str(
        path_file: Path,
        encoding: str = "utf-8",
) -> str:
    """ファイルのテキストを読み込む関数

    指定したパスのファイルから文字列を読み込む.

    Args:
        path_file: 読み込み対象ファイルのパス
        encoding: 文字エンコード

    Returns:
        読み込んだ文字列
    """
    with open(path_file, "r", encoding=encoding) as f:
        content = f.read()
    return content


def dict_to_json(
        dict_for_json: dict[Any, Any],
        path_file_json: Path,
        encoding: str = "utf-8",
) -> None:
    """ディクショナリ型からJSONファイルに書き出す関数

    指定したパスに.jsonファイルを作成する.

    Args:
        dict_for_json: .json書き出し対象のディクショナリ
        path_file_json: 作成する.jsonのパス
        encoding: 文字エンコード

    Returns:
        None
    """
    with open(path_file_json, "w", encoding=encoding) as f:
        json.dump(dict_for_json, f, ensure_ascii=False, indent=4)


def json_to_dict(
        path_file_json: Path,
        encoding: str = "utf-8",
) -> dict[Any, Any]:
    """JSONファイルを読み込む関数

    指定したパスの.jsonをディクショナリに変換する.

    Args:
        path_file_json: ディクショナリ変換対象の.jsonのパス
        encoding: 文字エンコード

    Returns:
        .jsonの内容のディクショナリ
    """
    with open(path_file_json, "r", encoding=encoding) as f:
        dict_from_json = json.load(f)
    return dict_from_json


def csv_to_list(
        path_file_csv: Path,
        encoding: str,
) -> list[list[str]]:
    """CSVファイルを読み込む関数

    ヘッダーが存在することを想定しており，読み込む時もスキップしない.

    Args:
        path_file_csv: 読み込み対象.csvのパス
        encoding: 文字エンコード

    Returns:
        .csvの内容のリスト
    """
    list_from_csv = []
    with open(path_file_csv, "r", encoding=encoding) as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            list_from_csv.append(row)
    return list_from_csv


def list_to_csv(
        list_for_csv: list[list[str]],
        path_file_csv: Path,
        encoding: str,
) -> None:
    """リスト型からCSVファイルに書き出す関数

    指定したパスに.csvファイルを作成する.

    Args:
        list_for_csv: .csv書き出し対象のリスト
        path_file_csv: 作成する.csvのパス
        encoding: 文字エンコード

    Returns:
        None
    """
    with open(path_file_csv, "w", encoding=encoding, newline="") as f:
        writer = csv.writer(f)
        writer.writerows(list_for_csv)
