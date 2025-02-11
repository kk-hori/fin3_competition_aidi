"""チャンク分割結果の各チャンクの埋め込みベクトルを取得した結果ファイルを作成するスクリプト

埋め込みベクトルは Azure OpenAI (AOAI) の Embedding モデルを実行することで取得する.
"""
import argparse

from az_openai import AOAIEmbeddingModel
from common.file_utils import dict_to_json, json_to_dict
from common.load_config import get_input_dir, get_output_dir

input_dir = get_input_dir()
output_dir = get_output_dir()


def parse_arguments() -> argparse.Namespace:
    """コマンドライン引数をパースする関数"""
    parser = argparse.ArgumentParser(
        description="指定した.jsonのチャンク分割のコンテンツを埋め込みベクトルを取得し結果ファイルを作成する"
    )

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="チャンク分割結果の.jsonファイル名を1個指定する"
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="result_embeddings.json",
        help="Embedding結果を格納する.jsonファイル名を1個指定する"
    )

    return parser.parse_args()


def main():
    args = parse_arguments()
    file_name_input = args.input
    file_name_output = args.output
    path_input_file = input_dir / file_name_input
    path_output_file = output_dir / file_name_output
    chunked_results = json_to_dict(path_input_file)
    embedding_results = {}
    obj_aoai_embedding = AOAIEmbeddingModel()

    for chunk_id, chunk_info in chunked_results.items():
        page_content = chunk_info["kwargs"]["page_content"]
        embedding_vector = obj_aoai_embedding.get_response(page_content)
        item = {
            "page_content": page_content,
            "embedding_vector": embedding_vector,
        }
        embedding_results[chunk_id] = item
        print(f"chunk_id: {chunk_id} is OK!")

    dict_to_json(embedding_results, path_output_file)


if __name__ == "__main__":
    main()
