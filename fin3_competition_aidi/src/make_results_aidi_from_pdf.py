"""Azure AI Document Intelligence (AIDI) の構造解析を実行し結果ファイルを作成するスクリプト

実行結果ファイルは以下の通り複数となる:
 - 無加工の実行結果(.json)
 - 実行結果を加工したコンテンツ(.md)
 - ドキュメントに含まれる画像(.png)

実行結果ファイルの格納ディレクトリ配下に以下のサブディレクトリが作成される:
 - json/: .jsonファイル格納用
 - md/: .mdファイル格納用
 - png/: .pngファイル格納用
"""
import argparse
import json
import mimetypes
from pathlib import Path

import fitz
from azure.ai.documentintelligence.models import AnalyzeResult
from common.file_utils import str_to_md_file
from common.load_config import get_input_dir, get_output_dir
from PIL import Image

from .az_ai_document_intelligence import AzAIDocumentIntelligence

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
    result_dict = result.to_dict()
    with open(path_file_json, "w", encoding=encoding) as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=4)


def crop_image_from_image(image_path, page_number, bounding_box):
    """
    Crops an image based on a bounding box.

    :param image_path: Path to the image file.
    :param page_number: The page number of the image to crop (for TIFF format).
    :param bounding_box: A tuple of (left, upper, right, lower) coordinates for the bounding box.
    :return: A cropped image.
    :rtype: PIL.Image.Image
    """
    with Image.open(image_path) as img:
        if img.format == "TIFF":
            # Open the TIFF image
            img.seek(page_number)
            img = img.copy()

        # The bounding box is expected to be in the format (left, upper, right, lower).
        cropped_image = img.crop(bounding_box)
        return cropped_image


def crop_image_from_pdf_page(pdf_path, page_number, bounding_box):
    """
    Crops a region from a given page in a PDF and returns it as an image.

    :param pdf_path: Path to the PDF file.
    :param page_number: The page number to crop from (0-indexed).
    :param bounding_box: A tuple of (x0, y0, x1, y1) coordinates for the bounding box.
    :return: A PIL Image of the cropped area.
    """
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)

    # Cropping the page. The rect requires the coordinates in the format (x0, y0, x1, y1).
    # The coordinates are in points (1/72 inch).
    bbx = [x * 72 for x in bounding_box]
    rect = fitz.Rect(bbx)
    pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72), clip=rect)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()

    return img


def crop_image_from_file(file_path, page_number, bounding_box):
    """
    Crop an image from a file.

    Args:
        file_path (str): The path to the file.
        page_number (int): The page number (for PDF and TIFF files, 0-indexed).
        bounding_box (tuple): The bounding box coordinates in the format (x0, y0, x1, y1).

    Returns:
        A PIL Image of the cropped area.
    """
    mime_type = mimetypes.guess_type(file_path)[0]

    if mime_type == "application/pdf":
        return crop_image_from_pdf_page(file_path, page_number, bounding_box)
    else:
        return crop_image_from_image(file_path, page_number, bounding_box)


def main():
    args = parse_arguments()
    file_name_input = args.input
    base_file_name = Path(file_name_input).stem
    path_file_input = input_dir / file_name_input

    json_dir_output = output_dir / "json"
    json_dir_output.mkdir(exist_ok=True)

    md_dir_output = output_dir / "md"
    md_dir_output.mkdir(exist_ok=True)

    png_dir_output = output_dir / "png"
    png_dir_output.mkdir(exist_ok=True)

    obj_aidi = AzAIDocumentIntelligence()
    result: AnalyzeResult = obj_aidi.get_analyzed_result()

    all_markdown = ""  # 最終的に出力したいMarkdown形式の文字列
    result_paragraphs = obj_aidi.get_paragraphs(result)
    result_sections = obj_aidi.get_sections(result)

    for sec in result_sections:
        if sec.startswith("/paragraphs/"):
            if result_paragraphs[sec]["role"] == "title":
                # titleならHeader1を付与
                all_markdown += "# " + result_paragraphs[sec]["content"] + "\n"
            elif result_paragraphs[sec]["role"] == "sectionHeading":
                # sectionHeadingならHeader2を付与
                all_markdown += "## " + \
                    result_paragraphs[sec]["content"] + "\n"
            else:
                all_markdown += result_paragraphs[sec]["content"]

        if sec.startswith("/figures/"):
            idx = int(sec.split("/")[-1])  # figureのIDを取得
            figure = result.figures[idx]
            if "boundingRegions" in figure:
                for i, br in enumerate(figure["boundingRegions"]):
                    page = br["pageNumber"]
                    bbox = br["polygon"]
                    bbox = (bbox[0], bbox[1], bbox[4], bbox[5])
                    image = crop_image_from_file(path_file_input, page-1, bbox)
                    path_output_png = png_dir_output / \
                        f"{base_file_name}_figure_{idx}_{i}.png"
                    image.save(path_output_png)
                    # 切り出した画像へのリンクをMarkdownに追加
                    all_markdown += f"![figure_{idx}_{i}]({path_output_png})"

        if sec.startswith("/tables/"):
            idx = int(sec.split("/")[-1])  # tableのIDを取得
            table = result.tables[idx]
            if "boundingRegions" in table:
                for i, br in enumerate(table["boundingRegions"]):
                    page = br["pageNumber"]
                    bbox = br["polygon"]
                    bbox = (bbox[0], bbox[1], bbox[4], bbox[5])
                    image = crop_image_from_file(path_file_input, page-1, bbox)
                    path_output_png = png_dir_output / \
                        f"{base_file_name}_table_{idx}_{i}.png"
                    image.save(path_output_png)
                    # 切り出した画像へのリンクをMarkdownに追加
                    all_markdown += f"![table_{idx}_{i}]({path_output_png})"

        all_markdown += "\n"
    path_output_md = md_dir_output / f"{base_file_name}_content.md"
    str_to_md_file(all_markdown, path_output_md)


if __name__ == "__main__":
    main()
