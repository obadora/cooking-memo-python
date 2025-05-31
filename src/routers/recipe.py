from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
import uuid
import requests
from bs4 import BeautifulSoup
from src.routers import task, done
import src.schemas.recipe as recipe_schema

router = APIRouter()
# 仮のDB（メモリ）
recipes_db = []
# 自作レシピ登録
@router.post("/recipes", response_model=recipe_schema.Recipe)
def create_recipe(recipe: recipe_schema.RecipeCreate):
    new_recipe = recipe_schema.Recipe(id=str(uuid.uuid4()), **recipe.dict())
    recipes_db.append(new_recipe)
    return new_recipe

# 自作レシピ一覧取得
@router.get("/recipes", response_model=List[recipe_schema.Recipe])
def list_recipes():
    return recipes_db