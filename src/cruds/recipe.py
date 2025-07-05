from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from src.models.recipe import Recipe, RecipePhoto, Ingredient, Step, CookingRecord, Tag, recipe_tags_table
from src.schemas.recipe import ScrapedRecipeData, SortOrder
from sqlalchemy import select, extract, desc, asc, func
from sqlalchemy.engine import Result
from sqlalchemy.orm import selectinload
from datetime import date

async def get_all_recipes(db: AsyncSession) -> Optional[Recipe]:
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
        )
        result: Result = await db.execute(stmt)
        recipe = result.scalars().all()
        return recipe
    except Exception as e:
        print(f"Error in crud_recipe.get: {e}")
        raise e

async def get_recipe_by_id(db: AsyncSession, id: int) -> Optional[Recipe]:
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
async def get_cooking_record(db: AsyncSession, id: int, date: date) -> Optional[CookingRecord]:
    result = await db.execute(
        select(CookingRecord).where(CookingRecord.recipe_id == id, CookingRecord.cooking_date == date)
    )
    cooking_record = result.scalar_one_or_none()
    return cooking_record

async def get_recipes_by_cooking_date(db: AsyncSession, cooking_date: date) -> List[Recipe]:
    """指定した日付で調理したレシピを全て取得"""
    try:
        # cooking_recordsから指定日付のrecipe_idを取得し、関連するレシピを取得
        stmt = select(Recipe).options(
            selectinload(Recipe.source_type),
            selectinload(Recipe.ingredients),
            selectinload(Recipe.steps),
            selectinload(Recipe.recipe_photos).selectinload(RecipePhoto.photo_type),
            selectinload(Recipe.cooking_records),
            selectinload(Recipe.categories),
            selectinload(Recipe.tags),
        ).join(CookingRecord).where(CookingRecord.cooking_date == cooking_date)
        
        result: Result = await db.execute(stmt)
        recipes = result.scalars().all()
        return list(recipes)
    except Exception as e:
        print(f"Error in get_recipes_by_cooking_date: {e}")
        raise e

async def get_recipes_by_month(db: AsyncSession, year: int, month: int) -> List[Recipe]:
    """指定した年月で調理したレシピを全て取得"""
    try:
        # cooking_recordsから指定年月のrecipe_idを取得し、関連するレシピを取得
        stmt = select(Recipe).options(
            selectinload(Recipe.source_type),
            selectinload(Recipe.ingredients),
            selectinload(Recipe.steps),
            selectinload(Recipe.recipe_photos).selectinload(RecipePhoto.photo_type),
            selectinload(Recipe.cooking_records),
            selectinload(Recipe.categories),
            selectinload(Recipe.tags),
        ).join(CookingRecord).where(
            extract('year', CookingRecord.cooking_date) == year,
            extract('month', CookingRecord.cooking_date) == month
        )
        
        result: Result = await db.execute(stmt)
        recipes = result.scalars().all()
        return list(recipes)
    except Exception as e:
        print(f"Error in get_recipes_by_month: {e}")
        raise e
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
    scraped_data: ScrapedRecipeData,
    cooking_date: date
) ->  Optional[Recipe]:
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
        cooking_date=cooking_date
    )
    db.add(cooking_record)
    
    await db.commit()
    await db.refresh(recipe)
    complete_recipe  = await get_recipe_by_id(db, recipe.id)
    return complete_recipe 
async def register_only_record(db: AsyncSession, recipe_id: int, cooking_date: date) -> None: 
    cooking_record = CookingRecord(
        recipe_id=recipe_id,
        cooking_date=cooking_date
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

async def search_recipes(
    db: AsyncSession,
    tag_ids: Optional[List[int]] = None,
    limit: Optional[int] = None,
    sort_by_created_at: Optional[bool] = False,
    sort_order: Optional[SortOrder] = SortOrder.desc
) -> List[Recipe]:
    """レシピを検索（AND条件でタグ絞り込み）"""
    try:
        stmt = select(Recipe).options(
            selectinload(Recipe.source_type),
            selectinload(Recipe.ingredients),
            selectinload(Recipe.steps),
            selectinload(Recipe.recipe_photos).selectinload(RecipePhoto.photo_type),
            selectinload(Recipe.cooking_records),
            selectinload(Recipe.categories),
            selectinload(Recipe.tags),
        )
        
        # タグIDで絞り込み（AND条件）
        if tag_ids and len(tag_ids) > 0:
            # 指定されたタグを全て持つレシピのIDを取得するサブクエリ
            subquery = (
                select(recipe_tags_table.c.recipe_id)
                .where(recipe_tags_table.c.tag_id.in_(tag_ids))
                .group_by(recipe_tags_table.c.recipe_id)
                .having(func.count(recipe_tags_table.c.tag_id) == len(tag_ids))
            )
            
            # メインクエリでサブクエリの結果に基づいて絞り込み
            stmt = stmt.where(Recipe.id.in_(subquery))
        
        # ソート
        if sort_by_created_at:
            if sort_order == SortOrder.desc:
                stmt = stmt.order_by(desc(Recipe.created_at))
            else:
                stmt = stmt.order_by(asc(Recipe.created_at))
        else:
            # デフォルトはID順
            if sort_order == SortOrder.desc:
                stmt = stmt.order_by(desc(Recipe.id))
            else:
                stmt = stmt.order_by(asc(Recipe.id))
        
        # 件数制限
        if limit:
            stmt = stmt.limit(limit)
        
        result: Result = await db.execute(stmt)
        recipes = result.scalars().all()
        return list(recipes)
    except Exception as e:
        print(f"Error in search_recipes: {e}")
        raise e

async def grant_tag_to_recipe(db: AsyncSession, recipe_id: int, tag_id: int) -> Optional[Recipe]:
    """レシピにタグを付与"""
    try:
        # レシピとタグの存在確認
        recipe = await get_recipe_by_id(db, recipe_id)
        if not recipe:
            raise ValueError(f"Recipe with id {recipe_id} not found")
        
        tag_result = await db.execute(select(Tag).where(Tag.id == tag_id))
        tag = tag_result.scalar_one_or_none()
        if not tag:
            raise ValueError(f"Tag with id {tag_id} not found")
        
        # 既に関連付けられているかチェック
        existing_stmt = select(recipe_tags_table).where(
            recipe_tags_table.c.recipe_id == recipe_id,
            recipe_tags_table.c.tag_id == tag_id
        )
        existing_result = await db.execute(existing_stmt)
        existing = existing_result.fetchone()
        
        if existing:
            raise ValueError(f"Recipe {recipe_id} already has tag {tag_id}")
        
        # タグを付与
        stmt = recipe_tags_table.insert().values(recipe_id=recipe_id, tag_id=tag_id)
        await db.execute(stmt)
        await db.commit()
        
        # 更新されたレシピを返す
        return await get_recipe_by_id(db, recipe_id)
    except Exception as e:
        print(f"Error in grant_tag_to_recipe: {e}")
        await db.rollback()
        raise e

async def remove_tag_from_recipe(db: AsyncSession, recipe_id: int, tag_id: int) -> Optional[Recipe]:
    """レシピからタグを削除"""
    try:
        # レシピの存在確認
        recipe = await get_recipe_by_id(db, recipe_id)
        if not recipe:
            raise ValueError(f"Recipe with id {recipe_id} not found")
        
        # 関連付けの存在確認
        existing_stmt = select(recipe_tags_table).where(
            recipe_tags_table.c.recipe_id == recipe_id,
            recipe_tags_table.c.tag_id == tag_id
        )
        existing_result = await db.execute(existing_stmt)
        existing = existing_result.fetchone()
        
        if not existing:
            raise ValueError(f"Recipe {recipe_id} does not have tag {tag_id}")
        
        # タグを削除
        stmt = recipe_tags_table.delete().where(
            recipe_tags_table.c.recipe_id == recipe_id,
            recipe_tags_table.c.tag_id == tag_id
        )
        await db.execute(stmt)
        await db.commit()
        
        # 更新されたレシピを返す
        return await get_recipe_by_id(db, recipe_id)
    except Exception as e:
        print(f"Error in remove_tag_from_recipe: {e}")
        await db.rollback()
        raise e