from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from src.models.recipe import Recipe, RecipePhoto, Ingredient, Step, CookingRecord
from src.schemas.recipe import ScrapedRecipeData
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm import selectinload
from datetime import date

async def get(db: AsyncSession, id: int) -> Optional[Recipe]:
    try:
        # 関連データを事前に読み込むためのクエリ
        stmt = select(Recipe).options(
            # 関連テーブルを事前に読み込み
            selectinload(Recipe.source_type),        # source_typeテーブル
            selectinload(Recipe.ingredients),        # ingredientsテーブル
            selectinload(Recipe.steps),             # stepsテーブル
            selectinload(Recipe.recipe_photos).selectinload(RecipePhoto.photo_type), # recipe_photosテーブル
            selectinload(Recipe.cooking_records), # cooking_recordsテーブル
            selectinload(Recipe.categories),        # categoriesテーブル（多対多）
            selectinload(Recipe.tags),              # tagsテーブル（多対多）
        ).where(Recipe.id == id)
        
        result: Result = await db.execute(stmt)
        recipe = result.scalar_one_or_none()
        return recipe
    except Exception as e:
        print(f"Error in crud_recipe.get: {e}")
        raise e
async def get_cooking_record(db: AsyncSession, id: int, date: date) -> Optional[Recipe]:
        result = await db.execute(
        select(CookingRecord).where(CookingRecord.recipe_id == id, CookingRecord.cooking_date == date)
    )
        recipe = result.scalar_one_or_none()
        return recipe
# crud/crud_recipe.py
async def get_by_source_url(db: AsyncSession, source_url: str):
    """URLでレシピを検索"""
    result = await db.execute(
        select(Recipe).where(Recipe.source_url == source_url)
    )
    return result.scalar_one_or_none()

# post    
async def create_from_scraped_data( 
    db: AsyncSession, 
    *, 
    scraped_data: ScrapedRecipeData
) -> Recipe:
    """スクレイピングデータからレシピを作成"""
    # webソースタイプを取得
    # web_source = db.query(SourceType).filter(SourceType.code == "web").first()
    # scraped_photo_type = db.query(PhotoType).filter(PhotoType.code == "scraped").first()
    
    # レシピ作成
    recipe = Recipe(
        title=scraped_data["title"],
        # description=scraped_data["description"],
        source_type_id=1,
        source_url=scraped_data["source_url"]
    )
    
    db.add(recipe)
    await db.flush()  # IDを取得するため
    
    # 材料追加
    for ing_data in scraped_data["ingredients"]:
        ingredient = Ingredient(recipe_id=recipe.id, name=ing_data)
        db.add(ingredient)
    
    # 手順追加
    for i, step_data in enumerate(scraped_data["steps"]):
        step = Step(recipe_id=recipe.id, step_number=i+1, instruction=step_data)
        db.add(step)
    
    # 写真追加
    recipe_photo = RecipePhoto(
            recipe_id=recipe.id,
            photo_url=scraped_data["photo_url"],
            photo_type_id=1,
            is_primary=True  # 最初の写真をプライマリに設定
        )
    db.add(recipe_photo)

    cooking_record = CookingRecord(
        recipe_id=recipe.id,
        cooking_date="2025-07-01"
    )
    db.add(cooking_record)
    
    await db.commit()
    await db.refresh(recipe)
    
    return recipe
async def register_only_record(db: AsyncSession, recipe_id: int) -> CookingRecord: 
    cooking_record = CookingRecord(
        recipe_id=recipe_id,
        cooking_date="2025-08-01"
    )
    db.add(cooking_record)
    
    await db.commit()
    return cooking_record

#delete
async def delete_recipe(db: AsyncSession, recipe: Recipe):
    """レシピを削除"""
    try:
        await db.delete(recipe)
        await db.commit()
        return True
    except Exception as e:
        print(f"Error in crud_recipe.delete_recipe: {e}")
        await db.rollback()
        raise e

async def delete_cooking_record(db: AsyncSession, cooking_record: CookingRecord):
    """日付で管理しているデータを削除"""
    try:
        await db.delete(cooking_record)
        await db.commit()
        return True
    except Exception as e:
        print(f"Error in crud_recipe.delete_recipe: {e}")
        await db.rollback()
        raise e