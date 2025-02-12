"""データを Elasticsearch に格納するスクリプト

別スクリプトで作成したチャンクや埋め込みベクトルの結果を Elasticsearch のデータに登録する.
本スクリプト実行前に,登録に使用するデータをinputディレクトリに決められたファイル名で格納しておく.
"""
from common.file_utils import json_to_dict
from common.load_config import get_input_dir, load_config
from elasticsearch import Elasticsearch

config = load_config()
input_dir = get_input_dir()

# Elasticsearch の各設定値を読み込む
URL = config["elasticsearch"]["url"]
INDEX_NAME_DOC = config["elasticsearch"]["data"]["index"]["name"]
DIMS_EMBEDDING = config["elasticsearch"]["data"]["index"]["dims_embedding"]

# コンペルールに伴う設定値を読み込む
DOCS_NUM = config["rules"]["docs_num"]


def main():

    # Elasticsearch に接続
    es = Elasticsearch(URL)

    # インデックス作成
    es.indices.create(
        index=INDEX_NAME_DOC,
        body={
            "settings": {
                "analysis": {
                    "analyzer": {
                        "kuromoji_analyzer": {
                            "type": "custom",
                            "tokenizer": "kuromoji_tokenizer",
                            "filter": ["kuromoji_baseform", "kuromoji_part_of_speech"]
                        }
                    }
                }
            },
            "mappings": {
                "dynamic": True,  # metadata のキーが消えても動的に対応
                "properties": {
                    "doc_id": {"type": "keyword"},  # 元のドキュメントID
                    "chunk_id": {"type": "integer"},  # チャンクの番号
                    "content": {
                        "type": "text",
                        "analyzer": "kuromoji_analyzer"  # kuromoji アナライザを適用
                    },
                    "embedding": {
                        "type": "dense_vector",
                        "dims": DIMS_EMBEDDING,  # embedding モデルに対応
                        "index": True,  # k-NN 検索を有効化
                        "similarity": "l2_norm"  # ユークリッド距離で類似度計算
                    },
                    "metadata": {
                        "type": "object",
                        "dynamic": True
                    }
                }
            }
        }
    )

    # 各ドキュメントのチャンク,埋め込みベクトル,およびメタデータを Elasticsearch に登録
    for doc_id in range(1, DOCS_NUM+1):
        file_name_doc = f"{str(doc_id)}.pdf"
        path_file_json = input_dir / f"{str(doc_id)}_embedding.json"
        data_for_es = json_to_dict(path_file_json)
        for key, value in data_for_es.items():
            chunk_id = int(key)
            chunk_content = value["content"]
            chunk_embedding_vector = value["embedding_vector"]
            chunk_metadata = value["metadata"]

            # Elasticsearch に登録
            doc = {
                "doc_id": file_name_doc,
                "chunk_id": chunk_id,
                "content": chunk_content,
                "embedding": chunk_embedding_vector,
                "metadata": chunk_metadata,
            }
            es.index(index=INDEX_NAME_DOC, body=doc)

    print("Document added successfully!")


if __name__ == "__main__":
    main()
