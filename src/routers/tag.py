from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.db import get_db
from src.cruds import tag as tag_crud
from src.schemas.recipe import TagResponse

router = APIRouter()

@router.get("/tags", response_model=List[TagResponse])
async def get_all_tags(db: AsyncSession = Depends(get_db)):
    """全てのタグを取得"""
    tags = await tag_crud.get_all_tags(db)
    return tags

@router.get("/tags/{tag_id}", response_model=TagResponse)
async def get_tag_by_id(tag_id: int, db: AsyncSession = Depends(get_db)):
    """IDでタグを取得"""
    tag = await tag_crud.get_tag_by_id(db, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag