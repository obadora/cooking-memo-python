import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def scrape_recipe_from_delish(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find('h1').text  # タイトルを取得
    ingredients = [ingredient.text for ingredient in soup.find_all(class_='ingredient')]  # 材料リスト
    steps = [step.text.strip() for step in soup.find_all("p", {"class": "step-desc"})]  # 手順
    # 最初の画像を取得
    video_tag = soup.find("video")  # 最初の<video>タグを取得
    photo_url = None
    if video_tag:
        photo_url = video_tag.get("poster")  # poster属性から画像URLを取得
    return {"title": title, "source_url": url, "ingredients": ingredients, "steps": steps, "photo_url": photo_url}

def scrape_recipe_from_kurashiru(url: str):
    """
    クラシルのレシピページから情報を取得する
    
    Args:
        url (str): クラシルのレシピページURL
    
    Returns:
        dict: レシピ情報を含む辞書
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # タイトルを取得
    title_element = soup.find('h1', class_='title')
    title = title_element.text.strip() if title_element else ""
    
    # 材料リストを取得
    ingredients = []
    ingredient_section = soup.find('section', class_='ingredients')
    if ingredient_section:
        ingredient_items = ingredient_section.find_all('li', class_='ingredient-list-item')
        for item in ingredient_items:
            # グループタイトルは除外
            if 'group-title' in item.get('class', []):
                continue
            
            name_element = item.find('a', class_='ingredient-name')
            quantity_element = item.find('span', class_='ingredient-quantity-amount')
            
            if name_element and quantity_element:
                ingredient_text = f"{name_element.text.strip()} {quantity_element.text.strip()}"
                ingredients.append(ingredient_text)
    
    # 手順を取得
    steps = []
    instructions_section = soup.find('section', class_='instructions')
    if instructions_section:
        step_items = instructions_section.find_all('li', class_='instruction-list-item')
        for item in step_items:
            content_element = item.find('span', class_='content')
            if content_element:
                steps.append(content_element.text.strip())
    
    # 最初の画像を取得（動画のポスター画像）
    photo_url = ""
    video_tag = soup.find("video")
    if video_tag:
        photo_url = video_tag.get("poster", "")
    
    return {
        "title": title,
        "source_url": url,
        "ingredients": ingredients,
        "steps": steps,
        "photo_url": photo_url
    }

def scrape_recipe(url: str):
    """URLパターンに基づいて適切なスクレイピングメソッドを選択"""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    
    print(f"スクレイピング開始: {url}, ドメイン: {domain}")
    
    if "delishkitchen.tv" in domain:
        return scrape_recipe_from_delish(url)
    elif "cookpad.com" in domain:
        # Cookpadは現在対応していないため、エラーを返す
        raise ValueError("Cookpadは現在対応していません")
    elif "kurashiru.com" in domain or "www.kurashiru.com" in domain:
        return scrape_recipe_from_kurashiru(url)
    else:
        raise ValueError(f"サポートされていないドメインです: {domain}")