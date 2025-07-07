from fastapi import APIRouter, HTTPException, Path, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
import src.schemas.recipe as recipe_schema
from src.cruds import recipe as crud_recipe
import src.services.scrape as services_scrape
from src.db import get_db
from datetime import date
from typing import List, Optional

router = APIRouter()
# 仮のDB（メモリ）
recipes_db = []
    
@router.get("/recipes", response_model=List[recipe_schema.RecipeDetailResponse])
async def read_recipe(
    db: AsyncSession = Depends(get_db)
):
    """レシピ詳細全取得（全関連データ含む）"""
    try:
        # 修正されたget関数（Eager Loading対応）を使用
        recipes = await crud_recipe.get_all_recipes(db)

        if not recipes:
            return []  # 空のリストを返す（404エラーではなく）

        return recipes
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in read_recipe: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
@router.get("/recipes/search", response_model=List[recipe_schema.RecipeDetailResponse])
async def search_recipes(
    tag_ids: Optional[List[int]] = Query(None, description="タグIDで絞り込み"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="取得件数上限"),
    sort_by_created_at: Optional[bool] = Query(False, description="作成日時でソートするか"),
    sort_order: Optional[recipe_schema.SortOrder] = Query(recipe_schema.SortOrder.desc, description="ソート順"),
    db: AsyncSession = Depends(get_db)
):
    """レシピを検索"""
    try:
        print(f"Search params - tag_ids: {tag_ids}, limit: {limit}, sort_by_created_at: {sort_by_created_at}, sort_order: {sort_order}")
        recipes = await crud_recipe.search_recipes(
            db=db,
            tag_ids=tag_ids,
            limit=limit,
            sort_by_created_at=sort_by_created_at,
            sort_order=sort_order
        )
        print(f"Found {len(recipes)} recipes")
        return recipes
    except Exception as e:
        print(f"Error in search_recipes: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
@router.get("/recipes/{recipe_id}", response_model=recipe_schema.RecipeDetailResponse)
async def read_recipe(
    recipe_id: int = Path(..., description="Recipe ID"),
    db: AsyncSession = Depends(get_db)
):
    """レシピ詳細取得（全関連データ含む）"""
    try:
        # 修正されたget関数（Eager Loading対応）を使用
        recipe = await crud_recipe.get_recipe_by_id(db, recipe_id)
        
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found") 
        return recipe
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in read_recipe: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
@router.get("/recipes/date/{cooking_date}", response_model=List[recipe_schema.RecipeDetailResponse])
async def get_recipes_by_date(
    cooking_date: date = Path(..., description="調理日付 (YYYY-MM-DD形式)"),
    db: AsyncSession = Depends(get_db)
):
    """指定した日付に調理したレシピを全て取得"""
    try:
        recipes = await crud_recipe.get_recipes_by_cooking_date(db, cooking_date)
        
        if not recipes:
            return []  # 空のリストを返す（404エラーではなく）
            
        return recipes
    except Exception as e:
        print(f"Error in get_recipes_by_date: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/cooking-records/month/{month_string}", response_model=List[recipe_schema.RecipeDetailResponse])
async def get_cooking_records_by_month(
    month_string: str = Path(..., description="年月 (YYYY-MM形式)", regex=r'^\d{4}-\d{2}$'),
    db: AsyncSession = Depends(get_db)
):
    """指定した年月に調理したレシピを全て取得"""
    try:
        # month_stringから年と月を抽出
        year, month = map(int, month_string.split('-'))
        
        recipes = await crud_recipe.get_recipes_by_month(db, year, month)
        
        if not recipes:
            return []  # 空のリストを返す（404エラーではなく）
            
        return recipes
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM format.")
    except Exception as e:
        print(f"Error in get_cooking_records_by_month: {e}")
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
        record = await crud_recipe.register_only_record(db, recipe_id, request.cooking_date)
        print("Returning recipe:", record)
        complete_recipe  = await crud_recipe.get_recipe_by_id(db, recipe_id)
        return complete_recipe 
    else:
        # スクレイピングを実行し、cooking_recordsにも登録する
        scraped_data = services_scrape.scrape_recipe(request.source_url)
        return await crud_recipe.create_from_scraped_data(db, scraped_data=scraped_data, cooking_date=request.cooking_date)

@router.delete("/recipe/{recipe_id}", response_model=None)
async def delete_recipe(
    recipe_id: int, db: AsyncSession = Depends(get_db)):
    recipe = await crud_recipe.get_recipe_by_id(db, recipe_id)
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

@router.post("/recipe/{recipe_id}/tag/{tag_id}", response_model=recipe_schema.RecipeDetailResponse)
async def grant_tag_to_recipe(
    recipe_id: int = Path(..., description="レシピID"),
    tag_id: int = Path(..., description="付与するタグID"),
    db: AsyncSession = Depends(get_db)
):
    """レシピにタグを付与（1つずつ付与）"""
    try:
        updated_recipe = await crud_recipe.grant_tag_to_recipe(db, recipe_id, tag_id)
        return updated_recipe
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        elif "already has tag" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error in grant_tag_to_recipe: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/recipe/{recipe_id}/tag/{tag_id}", response_model=recipe_schema.RecipeDetailResponse)
async def remove_tag_from_recipe(
    recipe_id: int = Path(..., description="レシピID"),
    tag_id: int = Path(..., description="削除するタグID"),
    db: AsyncSession = Depends(get_db)
):
    """レシピからタグを削除"""
    try:
        updated_recipe = await crud_recipe.remove_tag_from_recipe(db, recipe_id, tag_id)
        return updated_recipe
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        elif "does not have tag" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error in remove_tag_from_recipe: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/recipe/{recipe_id}/cooking-record/{cooking_record_id}/photos", response_model=List[recipe_schema.RecipePhotoResponse])
async def get_photos_by_cooking_record(
    recipe_id: int = Path(..., description="レシピID"),
    cooking_record_id: int = Path(..., description="調理記録ID"),
    db: AsyncSession = Depends(get_db)
):
    """指定レシピの指定調理記録の写真を取得"""
    try:
        photos = await crud_recipe.get_photos_by_cooking_record(db, recipe_id, cooking_record_id)
        return photos
    except Exception as e:
        print(f"Error in get_photos_by_cooking_record: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/recipe/{recipe_id}/photo/{photo_id}", response_model=recipe_schema.RecipePhotoResponse)
async def update_recipe_photo(
    recipe_id: int = Path(..., description="レシピID"),
    photo_id: int = Path(..., description="写真ID"),
    photo_data: recipe_schema.RecipePhotoUpdate = ...,
    db: AsyncSession = Depends(get_db)
):
    """レシピ写真を更新"""
    try:
        updated_photo = await crud_recipe.update_recipe_photo(db, recipe_id, photo_id, photo_data)
        return updated_photo
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error in update_recipe_photo: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
