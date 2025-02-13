"""Elasticsearch に登録したデータを削除するスクリプト

同じインデックス名で異なるデータが登録済かつ新たに登録し直す場合，登録前に本スクリプトを実行する.
"""
from common.load_config import load_config
from elasticsearch import Elasticsearch

config = load_config()

# Elasticsearch の各設定値を読み込む
URL = config["elasticsearch"]["url"]
INDEX_NAME_DOC = config["elasticsearch"]["data"]["index"]["name"]


def main():
    # Elasticsearch に接続
    es = Elasticsearch(URL)

    # 既存のインデックスを削除
    if es.indices.exists(index=INDEX_NAME_DOC):
        es.indices.delete(index=INDEX_NAME_DOC)
        print(f"Index '{INDEX_NAME_DOC}' deleted.")


if __name__ == "__main__":
    main()
