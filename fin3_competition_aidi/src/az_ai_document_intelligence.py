"""Azure AI Document Intelligence (AIDI) による機能をまとめたモジュール

各スクリプトで AIDI の処理が必要なときは本モジュールから呼び出す.

参考:
>https://qiita.com/nohanaga/items/1263f4a6bc909b6524c8
>https://nttdocomo-developers.jp/entry/2024/12/24/090000_2
"""
import os
from pathlib import Path

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.core.credentials import AzureKeyCredential
from common.load_config import load_config
from dotenv import load_dotenv
from typing_extensions import Any


class AzAIServices:
    """Azure AI servicesの機能をまとめたクラス

    各サービスのリソース利用のための共通機能をまとめる.

    Attributes:
        api_key: AIDIリソースのAPIキー
        endpoint: AIDIリソースのエンドポイント
    """

    def __init__(self):
        """イニシャライザ"""
        load_dotenv()
        self.api_key = os.getenv("AZURE_AI_SERVICES_API_KEY")
        self.endpoint = os.getenv("AZURE_AI_SERVICES_ENDPOINT")


class AzAIDocumentIntelligence(AzAIServices):
    """Azure AI Document Intelligence (AIDI) の機能をまとめたクラス

    API実行および実行結果を処理する機能をまとめる.
    APIによる解析対象のドキュメントはグラフや画像が埋め込まれた非構造的なPDFファイルを想定している.

    Attributes:
        document_intelligence_client: AIDIクライアント
    """

    def __init__(self):
        """イニシャライザ"""
        super().__init__()
        self.document_intelligence_client = DocumentIntelligenceClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.api_key),
        )
        config = load_config()
        self.config_aidi = config["az_ai_document_intelligence"]

    def get_analyzed_result(
            self,
            path_input_file: Path,
    ) -> AnalyzeResult:
        """ドキュメントの構造解析を実行する関数

        API実行によりレイアウトモデルの解析結果を取得する.

        Args:
            path_input_file: 解析対象ドキュメントのパス

        Returns:
            構造解析結果
        """
        with open(path_input_file, "rb") as f:
            poller = self.document_intelligence_client.begin_analyze_document(
                model_id=self.config_aidi["model_id"],
                output_content_format=self.config_aidi["output_content_format"],
            )
        result: AnalyzeResult = poller.result()
        return result

    def get_content(
            self,
            result: AnalyzeResult,
    ) -> str:
        """ドキュメント構造分析の実行結果からコンテンツ情報を取得する関数

        コンテンツのフォーマットは構造分析時に指定している.

        Args:
            result: AIDIによるドキュメントの構造解析結果

        Returns:
            解析結果のコンテンツ情報
        """
        content = result.content
        return content

    def get_sections(
            self,
            result: AnalyzeResult,
            layer_flag: bool = False,
    ) -> list[str]:
        """ドキュメント構造分析の実行結果から構造情報を取得する関数

        図表などのオブジェクトがドキュメントのどの部分に位置しているかについての情報を得られる.

        Args:
            result: AIDIによるドキュメントの構造解析結果
            layer_flag: 階層構造の情報を維持した結果とするか否かのフラグ

        Returns:
            セクションと各セクションの情報
        """
        sections = []
        for section in result.sections:
            if layer_flag is False:
                # sectionによる階層構造を無視するためextend
                sections.extend(section.elements)
            else:
                # sectionによる階層構造を維持するためappend
                sections.append(section.elements)
        return sections

    def get_paragraphs(
            self,
            result: AnalyzeResult,
    ) -> list[dict[str, str]]:
        """ドキュメント構造分析の実行結果から段落情報を取得する関数

        段落ごとのテキストブロックを抽出する.

        Args:
            result: AIDIによるドキュメントの構造解析結果

        Returns:
            解析結果の段落情報
        """
        paragraphs = []
        for idx, paragraph in enumerate(result.paragraphs):
            item = {
                "id": "/paragraphs/" + str(idx),
                "content": paragraph.content if paragraph.content else "",
                "role": paragraph.role if paragraph.role else "",
                "polygon": paragraph.get("boundingRegions")[0]["polygon"],
                "pageNumber": paragraph.get("boundingRegions")[0]["pageNumber"],
            }
            paragraphs.append(item)
        return paragraphs

    def get_tables(
        self,
        result: AnalyzeResult,
    ) -> list[dict[str, Any]]:
        """ドキュメント構造分析の実行結果から表情報を取得する関数

        表情報には「列と行の数」「行の範囲」「列の範囲」が含まれる.

        Args:
            result: AIDIによるドキュメントの構造解析結果

        Returns:
            解析結果の表情報
        """
        tables = []
        for _, table in enumerate(result.tables):
            cells = []
            for cell in table.cells:
                cells.append({
                    "row_index": cell.row_index,
                    "column_index": cell.column_index,
                    "content": cell.content,
                })
            tab = {
                "row_count": table.row_count,
                "column_count": table.column_count,
                "cells": cells,
            }
            tables.append(tab)
        return tables
