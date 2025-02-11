"""Azure OpenAI Service (AOAI) による機能をまとめたモジュール

各スクリプトで AOAI の処理が必要なときは本モジュールから呼び出す.
"""
import os

from dotenv import load_dotenv
from openai import AzureOpenAI


class AOAIModel:
    """Azure OpenAI Services (AOAI) のLLMモデルの機能をまとめたクラス

    各モデル利用のための共通機能をまとめる.

    Attributes:
        client: AOAIクライアント
    """

    def __init__(self):
        """イニシャライザ"""
        load_dotenv()
        self.client = AzureOpenAI(
            api_key=os.getenv("AOAI_API_KEY"),
            azure_endpoint=os.getenv("AOAI_ENDPOINT"),
            api_version=os.getenv("AOAI_API_VERSION"),
        )


class AOAIChatModel(AOAIModel):
    """Azure OpenAI Services (AOAI) の Chat モデルの機能をまとめたクラス

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
            "AOAI_DEPLOYMENT_ID_FOR_CHAT_COMPLETION")
        self.system_content = system_content

    def get_response_only_text(
            self,
            user_content: str,
            max_tokens: int = 4000,
            temperature: float = 0.2,
    ) -> str:
        """AOAIのChatモデルのAPIを実行し応答を取得するメソッド

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


class AOAIEmbeddingModel(AOAIModel):
    """Azure OpenAI Services (AOAI) の Embedding モデルの機能をまとめたクラス

    必要なパラメータを設定し, AOAIのAPIを実行する.

    Attributes:
        dep_id_embedding_comp: EmbeddingモデルID
    """

    def __init__(self):
        """イニシャライザ"""
        super().__init__()
        self.dep_id_embedding_comp = os.getenv(
            "AOAI_DEPLOYMENT_ID_FOR_EMBEDDING")

    def get_response(
            self,
            text: str,
    ) -> list[float]:
        """AOAIのEmbeddingモデルのAPIを実行し応答を取得するメソッド

        使用するモデルにより埋め込みの次元数が異なることに注意する.

        Args:
            text: 埋め込み対象のテキスト

        Returns:
            埋め込みベクトル
        """
        embedding_vector = self.client.embeddings.create(
            input=text,
            model=self.dep_id_embedding_comp,
        ).data[0].embedding

        return embedding_vector
