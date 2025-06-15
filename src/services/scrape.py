import requests
from bs4 import BeautifulSoup
from src.cruds import recipe as crud_recipe
from sqlalchemy.ext.asyncio import AsyncSession

def scrape_recipe(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find('h1').text  # タイトルを取得
    ingredients = [ingredient.text for ingredient in soup.find_all(class_='ingredient')]  # 材料リスト
    steps = [step.text.strip() for step in soup.find_all("p", {"class": "step-desc"})]  # 手順
    # 最初の画像を取得
    video_tag = soup.find("video")  # 最初の<video>タグを取得
    if video_tag:
        poster_url = video_tag.get("poster")  # poster属性から画像URLを取得
    return {"title": title, "ingredients": ingredients, "steps": steps, "poster_url": poster_url}

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