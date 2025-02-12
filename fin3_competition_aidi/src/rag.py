"""RAGの処理を定義するモジュール

各スクリプトで RAG の処理が必要なときは本モジュールから呼び出す.
"""
from openai_model import OpenAIChatModel


def generate_answer(
        query: str,
        information: str,
) -> str:
    """補足情報を元にクエリの回答を生成する関数

    回答の生成には Azure OpenAI のChatモデルを使用する.

    Args:
        query: クエリ
        information: 補足情報

    Returns:
        補足情報を元にしたクエリに対する回答
    """
    system_content = (
        "あなたは優秀なQAアシスタントです．"
        "ユーザーの指示に従い回答を生成してください．"
    )
    user_content = (
        "以下の<information>タグには，私が知りたい情報に関する企業のESG（環境・社会・ガバナンス）レポートや統合報告書の抜粋が含まれています．\n\n"
        f"<information>{information}</information>\n\n"
        "<information>タグの情報をもとに，以下の<question>タグの質問に対する回答を提供してください．\n"
        f"<question>{query}</question>\n\n"
        "ただし，質問への回答は以下の点に留意してください:\n"
        " - <information>タグの内容を参考にするが，回答に<information>タグを含めないこと\n"
        " - 数量で回答するべき質問の回答には単位をつけること\n"
        " - 質問に対して<information>タグにある情報で，質問に答えるための情報がない場合は「分かりません」と答えること"
    )
    obj_chat_model = OpenAIChatModel(system_content)
    answer = obj_chat_model.get_response_only_text(user_content)

    return answer


def process_answer(
        query: str,
        answer: str,
        max_tokens: int,
) -> str:
    """クエリに対して生成された回答を加工する関数

    最終的な回答に相応しい内容に加工する.

    Args:
        query: クエリ
        answer: クエリに対して生成された回答
        max_tokens: 最大トークン数

    Returns:
        加工後の回答
    """
    system_content = (
        "あなたはプロの編集者です．"
        "ユーザーが指示した通りに文章を編集してください．"
    )
    user_content = (
        "以下は質問文と，その質問文に対する回答文です．\n\n"
        "# 質問文\n"
        f"{query}\n\n"
        "# 回答文\n"
        f"{answer}\n\n"
        "回答文の中から最も簡潔に重要な内容のみ抽出してください．"
        "単語のみを回答しても構いません．\n\n"
        "# 留意事項\n"
        " - 句点(。)を含まないようにすること\n"
        " - 複数の回答がある場合は，読点(、)で区切ること\n"
        " - 質問文の問われ方に適した回答となっていること\n"
        "  - 例1: 理由について質問されていなければ，理由はいらず結論だけで良い\n"
        "  - 例2: 数量が問われている場合は単位とともに数量だけ回答する\n"
        "  - 例3: 単語が問われている場合は単語のみ答える\n"
        "  - 例4: 数量が問われていない場合は数量の情報を含めない\n"
        "  - 例5: 比較結果が問われいる場合は比較結果のみ答える\n"
        " - 文法の誤りを残さないこと\n"
        " - 「分かりません」「不明」という意味に近い回答の場合は「分かりません」と回答すること"
    )
    obj_chat_model = OpenAIChatModel(system_content)
    processed_answer = obj_chat_model.get_response_only_text(
        user_content=user_content,
        max_tokens=max_tokens,
        temperature=0,
    )

    return processed_answer
