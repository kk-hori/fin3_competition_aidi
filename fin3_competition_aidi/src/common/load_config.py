"""共通的な設定を取得する関数をまとめたモジュール

各スクリプトにおいて共通設定が必要な場合は，このモジュールに定義された関数を呼び出す．
"""
import json
import os
from pathlib import Path


def load_config() -> json:
    """プロジェクトディレクトリ内で定義したconfigファイルの内容を読み込む関数

    config.jsonを読み込む

    Args:
        None

    Returns:
        設定値が定義されたjsonオブジェクト
    """
    paht_config = os.path.join(os.path.dirname(
        __file__), "../../", "config.json")
    with open(paht_config, "r") as f:
        return json.load(f)


def get_input_dir() -> Path:
    """inputディレクトリのパスを取得する関数

    設定値はconfig.jsonに定義されている

    Args:
        None

    Returns:
        inputディレクトリのパス
    """
    config = load_config()
    return Path(config["directories"]["input"])


def get_output_dir() -> Path:
    """outputディレクトリのパスを取得する関数

    設定値はconfig.jsonに定義されている

    Args:
        None

    Returns:
        outputディレクトリのパス
    """
    config = load_config()
    return Path(config["directories"]["output"])
