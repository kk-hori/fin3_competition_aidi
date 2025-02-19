"""Elasticsearchで検索を実行する処理をまとめたモジュール

各スクリプトで Elasticsearch による検索処理が必要なときは本モジュールから呼び出す.
"""
from common.load_config import load_config
from elasticsearch import Elasticsearch
from typing_extensions import Any

config = load_config()

# Elasticsearch の各設定値を読み込む
URL = config["elasticsearch"]["url"]
INDEX_NAME_DOC = config["elasticsearch"]["data"]["index"]["name"]
DIMS_EMBEDDING = config["elasticsearch"]["data"]["index"]["dims_embedding"]


class ElasticsearchRetrivation:
    """Elasticsearchの検索処理をまとめたクラス

    登録済のデータに対し検索処理のメソッドが定義されている.

    Attributes:
        es: Elasticsearch クライアント
    """

    def __init__(self):
        """イニシャライザ"""
        self.es = Elasticsearch(URL)  # Elasticsearchに接続

    def retrieve_hybrid(
            self,
            query: str,
            query_vector: list[float],
            num_searches: int = 5,
            top: int = 3,
            num_candidates: int = 50,
            rate_vector_search: float = 0.7,
            minimum_should_match: int = 1,
    ) -> list[dict[str, Any]]:
        """ハイブリッド検索を実行するメソッド

        類似度検索およびキーワード検索を指定した比率で実行する.
        検索対象は全てのデータである.
        類似度アルゴリズムは knn である.

        Args:
            query: クエリ(キーワード検索対象)
            query_vector: クエリの埋め込みベクトル(類似度検索対象)
            num_searches: 内部的な検索件数
            top: 返却する検索結果件数
            num_candidates: 類似度計算の候補数
            rate_vector_search: 類似度検索の割合
            minimum_should_match: 最低のマッチ個数

        Returns:
            検索結果上位のデータ
        """
        rate_keyword_search = 1.0 - rate_vector_search  # キーワード検索の割合

        # ハイブリッド検索を実行
        response = self.es.search(
            index=INDEX_NAME_DOC,
            body={
                "size": top,
                "query": {
                    "bool": {
                        "should": [
                            {
                                "script_score": {
                                    "query": {
                                        "knn": {
                                            "field": "embedding",
                                            "query_vector": query_vector,
                                            "k": num_searches,
                                            "num_candidates": num_candidates
                                        }
                                    },
                                    "script": {
                                        "source": f"_score * {rate_vector_search}"
                                    }
                                }
                            },
                            {
                                "script_score": {
                                    "query": {
                                        "match": {
                                            "content": query
                                        }
                                    },
                                    "script": {
                                        "source": f"_score * {rate_keyword_search}"
                                    }
                                }
                            }
                        ],
                        "minimum_should_match": minimum_should_match
                    }
                }
            }
        )

        # 検索結果を返却
        results = []
        for hit in response["hits"]["hits"]:
            results.append(
                {
                    "doc_id": hit["_source"]["doc_id"],
                    "chunk_id": hit["_source"]["chunk_id"],
                    "content": hit["_source"]["content"],
                    "embedding": hit["_source"]["embedding"],
                    "metadata": hit["_source"]["metadata"],
                }
            )

        return results

    def retrieve_hybrid_with_filter(
            self,
            query: str,
            query_vector: list[float],
            doc_id_filter: str,
            num_searches: int = 5,
            top: int = 3,
            num_candidates: int = 50,
            rate_vector_search: float = 0.7,
            minimum_should_match: int = 1,
    ) -> list[dict[str, Any]]:
        """ハイブリッド検索を実行するメソッド

        類似度検索およびキーワード検索を指定した比率で実行する.
        検索対象はドキュメントIDによりフィルタリングされたデータである.
        類似度アルゴリズムは knn である.

        Args:
            query: クエリ(キーワード検索対象)
            query_vector: クエリの埋め込みベクトル(類似度検索対象)
            doc_id_filter: ドキュメントIDのフィルター条件
            num_searches: 内部的な検索件数
            top: 返却する検索結果件数
            num_candidates: 類似度計算の候補数
            rate_vector_search: 類似度検索の割合
            minimum_should_match: 最低のマッチ個数

        Returns:
            検索結果上位のデータ
        """
        rate_keyword_search = 1.0 - rate_vector_search  # キーワード検索の割合

        # ハイブリッド検索を実行
        response = self.es.search(
            index=INDEX_NAME_DOC,
            body={
                "size": top,
                "query": {
                    "bool": {
                        "must": [
                            # 指定された doc_id でフィルタリング
                            {"term": {"doc_id": doc_id_filter}}
                        ],
                        "should": [
                            {
                                "script_score": {
                                    "query": {
                                        "knn": {
                                            "field": "embedding",
                                            "query_vector": query_vector,
                                            "k": num_searches,
                                            "num_candidates": num_candidates
                                        }
                                    },
                                    "script": {
                                        "source": f"_score * {rate_vector_search}"
                                    }
                                }
                            },
                            {
                                "script_score": {
                                    "query": {
                                        "match": {
                                            "content": query
                                        }
                                    },
                                    "script": {
                                        "source": f"_score * {rate_keyword_search}"
                                    }
                                }
                            }
                        ],
                        "minimum_should_match": minimum_should_match
                    }
                }
            }
        )

        # 検索結果を返却
        results = []
        for hit in response["hits"]["hits"]:
            results.append(
                {
                    "doc_id": hit["_source"]["doc_id"],
                    "chunk_id": hit["_source"]["chunk_id"],
                    "content": hit["_source"]["content"],
                    "embedding": hit["_source"]["embedding"],
                    "metadata": hit["_source"]["metadata"],
                }
            )

        return results
