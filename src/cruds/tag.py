from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from src.models.recipe import Tag
from sqlalchemy import select
from sqlalchemy.engine import Result

async def get_all_tags(db: AsyncSession) -> List[Tag]:
    """全てのタグを取得"""
    try:
        stmt = select(Tag).order_by(Tag.name)
        result: Result = await db.execute(stmt)
        tags = result.scalars().all()
        return list(tags)
    except Exception as e:
        print(f"Error in get_all_tags: {e}")
        raise e

async def get_tag_by_id(db: AsyncSession, tag_id: int) -> Optional[Tag]:
    """IDでタグを取得"""
    try:
        stmt = select(Tag).where(Tag.id == tag_id)
        result: Result = await db.execute(stmt)
        tag = result.scalar_one_or_none()
        return tag
    except Exception as e:
        print(f"Error in get_tag_by_id: {e}")
        raise e

async def get_tag_by_name(db: AsyncSession, name: str) -> Optional[Tag]:
    """名前でタグを取得"""
    try:
        stmt = select(Tag).where(Tag.name == name)
        result: Result = await db.execute(stmt)
        tag = result.scalar_one_or_none()
        return tag
    except Exception as e:
        print(f"Error in get_tag_by_name: {e}")
        raise e

async def create_tag(db: AsyncSession, name: str) -> Tag:
    """新しいタグを作成"""
    try:
        tag = Tag(name=name)
        db.add(tag)
        await db.commit()
        await db.refresh(tag)
        return tag
    except Exception as e:
        print(f"Error in create_tag: {e}")
        await db.rollback()
        raise e

async def update_tag(db: AsyncSession, tag: Tag, name: str) -> Tag:
    """タグを更新"""
    try:
        tag.name = name
        await db.commit()
        await db.refresh(tag)
        return tag
    except Exception as e:
        print(f"Error in update_tag: {e}")
        await db.rollback()
        raise e

async def delete_tag(db: AsyncSession, tag: Tag) -> bool:
    """タグを削除"""
    try:
        await db.delete(tag)
        await db.commit()
        return True
    except Exception as e:
        print(f"Error in delete_tag: {e}")
        await db.rollback()
        raise e