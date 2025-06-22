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
        photo_url = video_tag.get("poster")  # poster属性から画像URLを取得
    return {"title": title, "source_url": url, "ingredients": ingredients, "steps": steps, "photo_url": photo_url}