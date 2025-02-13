"""コンペの提出データを作成するスクリプト

質問データを読み込み,RAGによって回答を生成する.
スクリプト実行前に,回答生成に使用するファイルをinputディレクトリに決められたファイル名で格納しておく.
"""
from az_openai_model import AOAIEmbeddingModel
from common.calc_utils import get_similar_vectors
from common.file_utils import csv_to_list, json_to_dict, list_to_csv
from common.load_config import get_input_dir, get_output_dir, load_config
from elasticsearch_retrieve_data import ElasticsearchRetrivation
from openai_model import OpenAIChatModel
from rag import generate_answer, process_answer

config = load_config()
input_dir = get_input_dir()
output_dir = get_output_dir()
MAX_TOKENS_ANSWER = config["rules"]["max_tokens_answer"]


def extract_company_name(
        text: str,
) -> str:
    """テキストから企業名を抽出する関数

    企業名の抽出に OpenAI のChatモデルを使用する.

    Args:
        text: 企業名を含むことが想定されるテキスト

    Returns:
        企業名
        企業名が抽出できない場合はハイフン(-)を想定
    """
    system_content = (
        "あなたは優秀な企業名抽出アシスタントです．"
        "ユーザーの指示に従い企業名を抽出してください．"
    )
    user_content = (
        "以下の<question>タグには，ある企業のESG（環境・社会・ガバナンス）レポートや統合報告書に関する質問文が含まれています．\n\n"
        f"<question>{text}</question>\n\n"
        "<question>タグの質問がどの企業に対する質問なのか知りたいため，企業名を抽出してください．\n"
        "ただし，抽出には以下の点に留意してください:\n"
        " - <question>タグの内容を参考にするが，回答に<question>タグを含めないこと\n"
        " - 回答には企業名のみ含めること\n"
        " - 企業名が含まれない場合はハイフン(-)と回答すること"
    )
    obj_chat_model = OpenAIChatModel(system_content)
    company_name = obj_chat_model.get_response_only_text(
        user_content, temperature=0)

    return company_name


def extract_company_name_from_query(
        query: str,
        company_name: str,
) -> str:
    """クエリに含まれる企業情報を除く関数

    企業情報を除いたクエリの作成に OpenAI のChatモデルを使用する.

    Args:
        query: クエリ
        company_name: 企業名

    Returns:
        企業名を除いたクエリ
    """
    system_content = (
        "あなたは優秀な編集者です．"
        "ユーザーの指示に従い文章を直してください．"
    )
    user_content = (
        f"<question>タグには，企業「{company_name}」のESG（環境・社会・ガバナンス）レポートや統合報告書の内容に関する質問が含まれています．\n\n"
        f"<question>{query}</question>\n\n"
        f"質問をより簡潔な表現にするために，企業「{company_name}」の情報を除いた質問に編集してください．\n"
        "ただし，編集には以下の点に留意してください:\n"
        " - <question>タグの内容を参考にするが，編集結果に<question>タグを含めないこと\n"
        " - それ以外は質問の内容を大きく意味を変えないこと"
    )
    obj_chat_model = OpenAIChatModel(system_content)
    query_non_company = obj_chat_model.get_response_only_text(
        user_content, temperature=0)

    return query_non_company


def main():
    path_query_file = input_dir / "query.csv"
    path_company_file = input_dir / "company_embedding.json"
    path_answer_file = output_dir / "predictions.csv"

    queries = csv_to_list(path_query_file)  # ヘッダー含む
    answers = []  # 生成された回答を格納する

    obj_aoai_embedding = AOAIEmbeddingModel()
    obj_es_retrievation = ElasticsearchRetrivation()

    dict_companies = json_to_dict(path_company_file)
    dict_for_similality = {}
    for doc_id, company_info in dict_companies.items():
        dict_for_similality[doc_id] = company_info["company_vector"]

    for row in queries[1:]:  # ヘッダーを飛ばす
        query_no = row[0]
        query = row[1]
        query_vector = obj_aoai_embedding.get_response(query)
        query_company = extract_company_name(query)

        if query_company != "-":
            query_company_vector = obj_aoai_embedding.get_response(
                query_company)
            doc_id_for_filter = get_similar_vectors(
                query_company_vector, dict_for_similality, top=1)[0][0]

            query_non_company = extract_company_name_from_query(
                query, query_company)
            query_vector_non_company = obj_aoai_embedding.get_response(
                query_non_company)
            es_search_results = obj_es_retrievation.retrieve_hybrid_with_filter(
                query=query_non_company,
                query_vector=query_vector_non_company,
                doc_id_filter=doc_id_for_filter,
                num_searches=10,
                top=5,
                num_candidates=100,
            )

        else:
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
