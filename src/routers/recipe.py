from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import src.schemas.recipe as recipe_schema
from src.cruds import recipe as crud_recipe
import src.services.scrape as services_scrape
from src.db import get_db
from datetime import date

router = APIRouter()
# 仮のDB（メモリ）
recipes_db = []

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

@router.post("/recipe/scrape", response_model=recipe_schema.RecipeDetailResponse)
async def scrape_and_save_recipe(
    request: recipe_schema.RecipeScrapeRequest,
    db: AsyncSession = Depends(get_db)
):
    print(f"Scraping recipe from URL: {request.source_url}")
    existing_recipe = await crud_recipe.get_by_source_url(db, request.source_url)
    if existing_recipe:
        recipe_id = existing_recipe.id
        record = await crud_recipe.register_only_record(db, recipe_id)
        print("Returning recipe:", record)
        complete_recipe  = await crud_recipe.get(db, recipe_id)
        return complete_recipe 
    else:
        # スクレイピングを実行し、cooking_recordsにも登録する
        scraped_data = services_scrape.scrape_recipe(request.source_url)
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