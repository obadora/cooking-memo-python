import cv2
import pytesseract
from PIL import Image
import numpy as np
import re
from typing import Dict, List, Optional
import io

def preprocess_image(image_data: bytes) -> np.ndarray:
    """
    画像を前処理してOCRの精度を向上させる
    """
    # バイト配列から画像を読み込み
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # グレースケール変換
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # ノイズ除去
    denoised = cv2.medianBlur(gray, 3)
    
    # 二値化（適応的閾値処理）
    binary = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # モルフォロジー変換でテキストを強調
    kernel = np.ones((1, 1), np.uint8)
    processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    return processed

def extract_text_from_image(image_data: bytes) -> str:
    """
    画像からテキストを抽出する
    """
    try:
        # 画像の前処理
        processed_image = preprocess_image(image_data)
        
        # OCR実行（日本語設定）
        custom_config = r'--oem 3 --psm 6 -l jpn'
        text = pytesseract.image_to_string(processed_image, config=custom_config)
        
        return text.strip()
    except Exception as e:
        print(f"OCR処理中にエラーが発生しました: {e}")
        return ""

def parse_recipe_text(text: str) -> Dict[str, any]:
    """
    OCRで抽出したテキストからレシピ情報を構造化する
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    recipe_data = {
        "title": "",
        "ingredients": [],
        "steps": [],
        "photo_url": ""
    }
    
    # タイトルの抽出（最初の行または最も大きなフォントの行）
    if lines:
        recipe_data["title"] = lines[0]
    
    # 材料セクションの検出
    ingredients_section = False
    steps_section = False
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        # 材料セクションの開始を検出
        if any(keyword in line for keyword in ["材料", "原材料", "食材", "ingredients"]):
            ingredients_section = True
            steps_section = False
            continue
        
        # 手順セクションの開始を検出
        if any(keyword in line for keyword in ["作り方", "手順", "調理法", "方法", "steps", "instructions"]):
            ingredients_section = False
            steps_section = True
            continue
        
        # 材料の抽出
        if ingredients_section:
            # 材料らしい行を検出（分量や単位が含まれている）
            if re.search(r'[0-9]+(g|ml|個|本|枚|切れ|大さじ|小さじ|カップ|cc)', line):
                recipe_data["ingredients"].append(line)
            # 材料名のみの行も追加
            elif len(line) > 1 and not re.search(r'^[0-9]+\.', line):
                recipe_data["ingredients"].append(line)
        
        # 手順の抽出
        if steps_section:
            # 手順番号が含まれている行
            if re.search(r'^[0-9]+\.', line) or re.search(r'^\([0-9]+\)', line):
                recipe_data["steps"].append(line)
            # または動詞で始まる行（調理手順らしい）
            elif re.search(r'^(切|焼|煮|炒|混|加|入|取|置|冷)', line):
                recipe_data["steps"].append(line)
    
    # 材料と手順が空の場合、シンプルなパターンで再試行
    if not recipe_data["ingredients"] and not recipe_data["steps"]:
        recipe_data = _simple_parse_fallback(lines)
    
    return recipe_data

def _simple_parse_fallback(lines: List[str]) -> Dict[str, any]:
    """
    シンプルなパターンでのフォールバック解析
    """
    recipe_data = {
        "title": "",
        "ingredients": [],
        "steps": [],
        "photo_url": ""
    }
    
    if lines:
        recipe_data["title"] = lines[0]
    
    # 行を材料と手順に分類
    for line in lines[1:]:
        # 数量を含む行は材料の可能性が高い
        if re.search(r'[0-9]+(g|ml|個|本|枚|切れ|大さじ|小さじ|カップ|cc)', line):
            recipe_data["ingredients"].append(line)
        # 動詞で始まる行は手順の可能性が高い
        elif re.search(r'^(切|焼|煮|炒|混|加|入|取|置|冷)', line):
            recipe_data["steps"].append(line)
        # 番号付きの行は手順
        elif re.search(r'^[0-9]+\.', line) or re.search(r'^\([0-9]+\)', line):
            recipe_data["steps"].append(line)
    
    return recipe_data

def extract_recipe_from_book_photo(image_data: bytes) -> Dict[str, any]:
    """
    書籍写真からレシピ情報を抽出するメイン関数
    """
    # OCRでテキストを抽出
    extracted_text = extract_text_from_image(image_data)
    
    if not extracted_text:
        raise ValueError("画像からテキストを抽出できませんでした")
    
    # テキストを構造化
    recipe_data = parse_recipe_text(extracted_text)
    
    # 最低限の情報がない場合はエラー
    if not recipe_data["title"] and not recipe_data["ingredients"] and not recipe_data["steps"]:
        raise ValueError("レシピ情報を抽出できませんでした")
    
    return recipe_data