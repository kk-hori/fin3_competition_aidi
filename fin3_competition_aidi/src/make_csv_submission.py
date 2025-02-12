"""コンペの提出データを作成するスクリプト

質問データを読み込み,RAGによって回答を生成する.
スクリプト実行前に,回答生成に使用するファイルをinputディレクトリに決められたファイル名で格納しておく.
"""
from az_openai import AOAIEmbeddingModel
from common.file_utils import csv_to_list, json_to_dict, list_to_csv
from common.load_config import get_input_dir, get_output_dir, load_config
from elasticsearch_retrieve_data import ElasticsearchRetrivation
from rag import generate_answer, process_answer

config = load_config()
input_dir = get_input_dir()
output_dir = get_output_dir()
MAX_TOKENS_ANSWER = config["rules"]["max_tokens_answer"]


def main():
    path_query_file = input_dir / "query.csv"
    path_answer_file = output_dir / "predictions.csv"

    queries = csv_to_list(path_query_file)  # ヘッダー含む
    answers = []  # 生成された回答を格納する

    obj_aoai_embedding = AOAIEmbeddingModel()
    obj_es_retrievation = ElasticsearchRetrivation()

    for row in queries[1:]:  # ヘッダーを飛ばす
        query_no = row[0]
        query = row[1]
        query_vector = obj_aoai_embedding.get_response(query)
        es_search_results = obj_es_retrievation.retrieve_hybrid(
            query=query,
            query_vector=query_vector,
            num_searches=10,
            top=5,
            num_candidates=100,
        )
        infomation_for_answer = ""
        for i, result in enumerate(es_search_results):
            content = result["content"]
            infomation_for_answer += "\n" + \
                f"{i+1}個目の情報:" + "\n============\n" + f"{content}" + "\n"
        answer = generate_answer(query, infomation_for_answer)
        processed_answer = process_answer(
            query, answer, max_tokens=MAX_TOKENS_ANSWER)
        if (processed_answer == "") or (processed_answer is None):
            processed_answer = "分かりません"
        print(f"{query_no}: {processed_answer}")
        answers.append([query_no, processed_answer])

    list_to_csv(answers, path_answer_file)


if __name__ == "__main__":
    main()
