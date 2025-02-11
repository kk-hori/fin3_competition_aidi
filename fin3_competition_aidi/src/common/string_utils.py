"""共通的な文字列操作の機能をまとめたモジュール

各スクリプトにおける文字列操作は，本モジュールに定義された機能を呼び出す.
"""
import tiktoken


def count_tokens(
        text: str,
        model_name: str,
) -> int:
    """トークン数をカウントする関数

    指定するモデルによりエンコーディング方法が異なることに注意する.

    Args:
        text: トークン数カウント対象のテキスト
        model_name: エンコードに使用するモデル名

    Returns:
        トークン数
    """
    encoding = tiktoken.encoding_for_model(
        model_name=model_name
    )
    return len(encoding.encode(text))
