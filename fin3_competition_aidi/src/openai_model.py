"""OpenAI による機能をまとめたモジュール

各スクリプトで OpenAI の処理が必要なときは本モジュールから呼び出す.
"""
import os

from dotenv import load_dotenv
from openai import OpenAI


class OpenAIModel:
    """OpenAI のLLMモデルの機能をまとめたクラス

    各モデル利用のための共通機能をまとめる.

    Attributes:
        client: OpenAIクライアント
    """

    def __init__(self):
        """イニシャライザ"""
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )


class OpenAIChatModel(OpenAIModel):
    """OpenAI の Chat モデルの機能をまとめたクラス

    必要なパラメータを設定し, AOAIのAPIを実行する.

    Attributes:
        dep_id_chat_comp: ChatモデルID
        system_content: システムプロンプト
    """

    def __init__(
            self,
            system_content: str,
    ):
        """イニシャライザ

        Args:
            system_content: システムプロンプト
        """
        super().__init__()
        self.dep_id_chat_comp = os.getenv(
            "OPENAI_CHAT_MODEL")
        self.system_content = system_content

    def get_response_only_text(
            self,
            user_content: str,
            max_tokens: int = 4000,
            temperature: float = 0.2,
    ) -> str:
        """OpenAIのChatモデルのAPIを実行し応答を取得するメソッド

        インプットはテキストのみを想定する.
        Chat履歴をリセットしてAPIを実行する.

        Args:
            user_content: ユーザープロンプト
            max_tokens: Chatモデル入出力合計トークン数の上限値
            temperature: Chatモデル応答のランダム性(創造性)

        Returns:
            Chatモデルが生成した応答テキスト
        """
        messages = [
            {"role": "system", "content": self.system_content},
            {"role": "user", "content": user_content},
        ]
        response = self.client.chat.completions.create(
            model=self.dep_id_chat_comp,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        ).choices[0].message.content

        return response
