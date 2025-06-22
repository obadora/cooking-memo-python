from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Tuple, Optional
from src.models.recipe import Recipe, RecipePhoto, SourceType, PhotoType, Ingredient, Step
from src.schemas.recipe import ScrapedRecipeData
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm import selectinload

# async def get(db: AsyncSession, id: int) -> Optional[Recipe]:
#     result: Result = await (
#         db.execute(
#             select(Recipe).filter(Recipe.id == id)
#         )
#     )
#     return result.scalar_one_or_none()
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
# 軽量版：関連データなしでレシピのみ取得
async def get_basic(db: AsyncSession, id: int) -> Optional[Recipe]:
    """関連データなしでレシピの基本情報のみ取得"""
    try:
        stmt = select(Recipe).where(Recipe.id == id)
        result: Result = await db.execute(stmt)
        recipe = result.scalar_one_or_none()
        return recipe
    except Exception as e:
        print(f"Error in crud_recipe.get_basic: {e}")
        raise e
    
# crud/crud_recipe.py
async def get_by_source_url(db: AsyncSession, source_url: str):
    """URLでレシピを検索"""
    result = await db.execute(
        select(Recipe).where(Recipe.source_url == source_url)
    )
    return result.scalar_one_or_none()

async def save_recipe(db: AsyncSession, recipe: Recipe) -> Recipe:
    """レシピを保存"""
    try:
        db.add(recipe)
        await db.commit()
        await db.refresh(recipe)
        return recipe
    except Exception as e:
        print(f"Error in crud_recipe.save_recipe: {e}")
        await db.rollback()
        raise e
    
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
        # source_url=scraped_data["source_url"]
    )
    
    db.add(recipe)
    await db.flush()  # IDを取得するため
    
    # 材料追加
    for ing_data in scraped_data["ingredients"]:
        ingredient = Ingredient(recipe_id=recipe.id, name=ing_data)
        db.add(ingredient)
    
    # 手順追加
    # for step_data in scraped_data["steps"]:
    #     step = Step(recipe_id=recipe.id, **step_data)
    #     db.add(step)
    
    # # 写真追加
    # for photo_data in scraped_data.photos:
    #     photo = RecipePhoto(
    #         recipe_id=recipe.id,
    #         photo_type_id=scraped_photo_type.id if scraped_photo_type else None,
    #         **photo_data
    #     )
    #     db.add(photo)
    
    await db.commit()
    await db.refresh(recipe)
    
    return recipe