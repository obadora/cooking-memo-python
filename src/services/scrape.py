import requests, re
from bs4 import BeautifulSoup
from src.cruds import recipe as crud_recipe
from sqlalchemy.ext.asyncio import AsyncSession

def scrape_recipe(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # タイトルを取得
    title = soup.find('h1').text.strip() if soup.find('h1') else "タイトル不明"
    
    # 材料リストを取得（シンプル版）
    ingredients = []
    
    # 材料リスト全体を取得
    ingredient_list = soup.find('ul', class_='ingredient-list')
    if ingredient_list:
        list_items = ingredient_list.find_all('li')
        
        for item in list_items:
            # グループヘッダーは無視
            if 'ingredient-group__header' in item.get('class', []):
                continue
            
            # 通常の材料アイテム
            if 'ingredient' in item.get('class', []):
                name_elem = item.find(class_='ingredient-name')
                serving_elem = item.find(class_='ingredient-serving')
                
                if name_elem:
                    name = name_elem.text.strip()
                    quantity = serving_elem.text.strip() if serving_elem else ''
                    
                    ingredient_data = {
                        'name': name,
                        'quantity': quantity
                    }
                    
                    ingredients.append(ingredient_data)
    
    # 手順を取得（番号付きで）
    steps = [] # List<dict>
    step_elements = soup.find_all("p", {"class": "step-desc"})
    
    for i, step in enumerate(step_elements, 1):
        step_text = step.text.strip()
        
        # 既に番号が含まれているかチェック
        step_number_match = re.match(r'^(\d+)\.?\s*(.+)', step_text)
        if step_number_match:
            step_number = int(step_number_match.group(1))
            instruction = step_number_match.group(2)
        else:
            # 番号がない場合は自動採番
            step_number = i
            instruction = step_text
        
        steps.append({
            'step_number': step_number,
            'instruction': instruction
        })
    
    # 画像を取得
    photo_url = None
    video_tag = soup.find("video")
    if video_tag:
        photo_url = video_tag.get("poster")
    
    # videoがない場合は最初のimg要素を探す
    if not photo_url:
        img_tag = soup.find("img")
        if img_tag:
            photo_url = img_tag.get("src") or img_tag.get("data-src")
    
    return {
        "title": title,
        "ingredients": ingredients,
        "steps": steps,
        "photo_url": photo_url,
        "source_url": url
    }

# async def scrape_and_save_recipe(url: str, db: AsyncSession, force_save: bool = False):
#     """スクレイピング + DB保存"""
#     # 重複チェック: 同じURLのレシピが既に存在するかチェック
#     # TODO: force_saveは消す
#     if not force_save:
#         existing_recipe = await crud_recipe.get_by_source_url(db, url)
#         if existing_recipe:
#             return {
#                 "exists": True,
#                 "recipe": existing_recipe,
#                 "message": "Recipe already exists with this URL"
#             }
    
#     # スクレイピング実行
#     scraped_data = scrape_recipe(url)
    
#     # レシピ基本情報の作成
#     recipe_data = recipe_schema.RecipeCreate(
#         title=scraped_data["title"],
#         description="",  # 必要に応じて設定
#         source_type_id=1,  # 'web'の source_type_id（事前に設定必要）
#         source_url=url
#     )