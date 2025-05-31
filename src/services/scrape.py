import requests
from bs4 import BeautifulSoup

def scrape_recipe(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find('h1').text  # タイトルを取得
    ingredients = [ingredient.text for ingredient in soup.find_all(class_='ingredient')]  # 材料リスト
    steps = [step.text.strip() for step in soup.find_all("p", {"class": "step-desc"})]  # 手順

    return {"title": title, "ingredients": ingredients, "steps": steps}