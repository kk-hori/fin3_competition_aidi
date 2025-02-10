"""Azure AI Document Intelligence (AIDI) の構造解析を実行し結果ファイルを作成するスクリプト

実行結果ファイルは以下の通り複数となる:
 - 無加工の実行結果(.json)
 - 実行結果を加工したコンテンツ(.md)
"""
import argparse
import json
from pathlib import Path

from az_ai_document_intelligence import AzAIDocumentIntelligence
from azure.ai.documentintelligence.models import AnalyzeResult
from common.file_utils import str_to_md_file
from common.load_config import get_input_dir, get_output_dir

input_dir = get_input_dir()
output_dir = get_output_dir()


def parse_arguments() -> argparse.Namespace:
    """コマンドライン引数をパースする関数"""
    parser = argparse.ArgumentParser(
        description="指定した.pdfをAIDIで構造解析し実行結果ファイル群を作成する"
    )

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="構造解析対象の.pdfファイル名を1個指定する"
    )

    return parser.parse_args()


def result_to_json(
        result: AnalyzeResult,
        path_file_json: Path,
        encoding: str = "utf-8",
) -> None:
    """AIDI実行結果をJSONファイルに書き出す関数

    指定したパスに.jsonファイルを作成する.

    Args:
        result: AIDIによるドキュメントの構造解析結果
        path_file_json: 作成する.jsonのパス
        encoding: 文字エンコード

    Returns:
        None
    """
    result_dict = result.as_dict()
    with open(path_file_json, "w", encoding=encoding) as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=4)


def main():
    args = parse_arguments()
    file_name_input = args.input
    base_file_name = Path(file_name_input).stem
    path_input_file = input_dir / file_name_input
    path_output_json = output_dir / f"{base_file_name}.json"
    path_output_md = output_dir / f"{base_file_name}.md"
    obj_aidi = AzAIDocumentIntelligence()
    result: AnalyzeResult = obj_aidi.get_analyzed_result(path_input_file)
    content = obj_aidi.get_content(result)
    result_to_json(result, path_output_json)
    str_to_md_file(content, path_output_md)


if __name__ == "__main__":
    main()
