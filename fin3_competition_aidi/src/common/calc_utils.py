"""共通的な数学計算の処理をまとめたモジュール

各スクリプトにおける数学計算は,本モジュールに定義された関数を呼び出す.
"""
import numpy as np


def cos_similarity(
    vec_a: list[float],
    vec_b: list[float],
) -> float:
    """類似度を算出する関数

    コサイン類似度を対象とする.

    Args:
        vec_a: 類似度計算対象のベクトル
        vec_b: 類似度計算対象のベクトル

    Returns:
        コサイン類似度
    """
    a = np.array(vec_a)
    b = np.array(vec_b)

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def get_similar_vectors(
    vector_origin: list[float],
    dict_vectors: dict[int | str, float],
    top: int,
) -> list[tuple[int | str, float]]:
    """類似度検索し上位の結果を取得する関数

    取得する件数を指定する.

    Args:
        vector_origin: 検索対象ベクトル
        dict_vectors: 類似候補のベクトル群
        top: 取得する検索結果の上位件数

    Returns:
        上位の検索結果
    """
    list_similarities = []
    for key, vector in dict_vectors.items():
        score = cos_similarity(vector_origin, vector)
        list_similarities.append((key, score))
    list_similarities.sort(key=lambda x: x[1], reverse=True)  # 類似度スコアが高い順にソート

    return list_similarities[0:top]
