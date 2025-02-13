"""Markdownファイルのテキストから企業情報をまとめたJSONファイルを作成するスクリプト

企業名および企業名の埋め込みベクトルを取得する.
スクリプト実行前に,JSONファイル作成に使用するファイルをinputディレクトリに決められたファイル名で格納しておく.
"""
from pathlib import Path

from az_openai_model import AOAIEmbeddingModel
from common.file_utils import dict_to_json, file_to_str
from common.load_config import get_input_dir, get_output_dir, load_config
from openai_model import OpenAIChatModel

config = load_config()
DOCS_NUM = config["rules"]["docs_num"]
input_dir = get_input_dir()
output_dir = get_output_dir()


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
        "以下の<information>タグには，私が知りたい情報に関する企業のESG（環境・社会・ガバナンス）レポートや統合報告書に関する内容の一部です．\n\n"
        f"<information>{text}</information>\n\n"
        "<information>タグの情報がどの企業のレポートや報告書なのか企業名を抽出してください．\n"
        "ただし，抽出には以下の点に留意してください:\n"
        " - <information>タグの内容を参考にするが，回答に<information>タグを含めないこと\n"
        " - 回答には企業名のみ含めること\n"
        " - 企業名は可能な限り略称ではなく正式名称とすること\n"
        " - 企業名が含まれない場合はハイフン(-)と回答すること"
    )
    obj_chat_model = OpenAIChatModel(system_content)
    company_name = obj_chat_model.get_response_only_text(
        user_content, temperature=0)

    return company_name


def main():
    dict_for_json = {}
    obj_embedding_model = AOAIEmbeddingModel()

    for doc_id in range(1, DOCS_NUM+1):
        file_name_doc = f"{str(doc_id)}.pdf"
        path_file_md = input_dir / f"{str(doc_id)}.md"
        md_text = file_to_str(path_file_md)
        md_text_500 = md_text[:500]  # 最初の500文字のみ取得
        company_name = extract_company_name(md_text_500)
        company_vector = obj_embedding_model.get_response(company_name)
        item = {
            "company_name": company_name,
            "company_vector": company_vector,
        }
        dict_for_json[file_name_doc] = item

    path_output_file = output_dir / "company_embedding.json"
    dict_to_json(dict_for_json, path_output_file)


if __name__ == "__main__":
    main()
