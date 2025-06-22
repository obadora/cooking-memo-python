from fastapi import APIRouter, HTTPException, Query, Path, Depends,FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List
import uuid
import requests
from bs4 import BeautifulSoup
from src.routers import task, done
import src.schemas.recipe as recipe_schema
from src.cruds import recipe as crud_recipe
from src.schemas.recipe import SourceType, PhotoType
from src.models.recipe import Recipe, Ingredient, Step, RecipePhoto
import src.services.scrape as services_scrape
from src.models.recipe import Recipe, RecipePhoto  
from src.db import get_db
from datetime import date

router = APIRouter()
# 仮のDB（メモリ）
recipes_db = []
# 自作レシピ登録
# @router.post("/recipes", response_model=recipe_schema.RecipeResponse)
# def create_recipe(recipe: recipe_schema.RecipeCreate):
#     new_recipe = recipe_schema.Recipe(id=str(uuid.uuid4()), **recipe.dict())
#     recipes_db.append(new_recipe)
#     return new_recipe

# 自作レシピ一覧取得
# @router.get("/recipes", response_model=List[recipe_schema.Recipe])
# def list_recipes():
#     return recipes_db
# レシピ関連
# レシピ詳細取得（基本情報のみ）
@router.get("/recipes/{recipe_id}/basic")
async def read_recipe_basic(
    recipe_id: int = Path(..., description="Recipe ID"),
    db: AsyncSession = Depends(get_db)
):
    """レシピ基本情報取得（関連データなし）"""
    try:
        recipe = await crud_recipe.get_basic(db, recipe_id)
        
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return recipe
        # 基本情報のみを辞書として返す
        # return {
        #     "id": recipe.id,
        #     "title": recipe.title,
        #     "description": recipe.description,
        #     "cook_time": recipe.cook_time,
        #     "servings": recipe.servings,
        #     "source_type_id": recipe.source_type_id,
        #     "source_url": recipe.source_url,
        #     "source_recipe_id": recipe.source_recipe_id,
        #     "source_book_title": recipe.source_book_title,
        #     "source_page": recipe.source_page,
        #     "manual_identifier": recipe.manual_identifier,
        #     "cooking_date": recipe.cooking_date,
        #     "cooking_memo": recipe.cooking_memo,
        #     "rating": recipe.rating,
        #     "created_at": recipe.created_at,
        #     "updated_at": recipe.updated_at
        # }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in read_recipe_basic: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# @router.get("/recipes/{recipe_id}", response_model=recipe_schema.RecipeResponse)
# async def read_recipe(
#     recipe_id: int,
#     db: AsyncSession = Depends(get_db)
# ):
#     """レシピ詳細取得"""
#     recipe = await crud_recipe.get(db, recipe_id)
#     if not recipe:
#         raise HTTPException(status_code=404, detail="Recipe not found")
#     return recipe
# レシピ詳細取得（完全版 - Eager Loading使用）
@router.get("/recipes/{recipe_id}", response_model=recipe_schema.RecipeDetailResponse)
async def read_recipe(
    recipe_id: int = Path(..., description="Recipe ID"),
    db: AsyncSession = Depends(get_db)
):
    """レシピ詳細取得（全関連データ含む）"""
    try:
        # 修正されたget関数（Eager Loading対応）を使用
        recipe = await crud_recipe.get(db, recipe_id)
        
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        return recipe
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in read_recipe: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/recipe/scrape", response_model=None)
async def scrape_and_save_recipe(
    source_url: str,
    db: AsyncSession = Depends(get_db)
):
    
    existing_recipe = await crud_recipe.get_by_source_url(db, source_url)
    if existing_recipe:
        recipe_id = existing_recipe.id
        return await crud_recipe.register_only_record(db, recipe_id)
    else:
        # スクレイピングを実行し、cooking_recordsにも登録する
        scraped_data = services_scrape.scrape_recipe(source_url)
        return await crud_recipe.create_from_scraped_data(db, scraped_data=scraped_data)

@router.delete("/recipe/{recipe_id}", response_model=None)
async def delete_recipe(
    recipe_id: int, db: AsyncSession = Depends(get_db)):
    recipe = await crud_recipe.get(db, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return await crud_recipe.delete_recipe(db, recipe)

@router.delete("/recipe/record/{recipe_id}/{date}", response_model=None)
async def delete_cooking_record(
    recipe_id: int, date: date, db: AsyncSession = Depends(get_db)):
    cooking_record = await crud_recipe.get_cooking_record(db, recipe_id, date)
    if cooking_record is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return await crud_recipe.delete_cooking_record(db, cooking_record)