from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.db import get_db
from src.cruds import tag as tag_crud
from src.schemas.recipe import TagResponse, TagCreate

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

@router.post("/tag", response_model=TagResponse)
async def create_tag(tag_data: TagCreate, db: AsyncSession = Depends(get_db)):
    """新しいタグを作成"""
    existing_tag = await tag_crud.get_tag_by_name(db, tag_data.name)
    if existing_tag:
        raise HTTPException(status_code=400, detail="Tag with this name already exists")
    
    tag = await tag_crud.create_tag(db, tag_data.name)
    return tag

@router.put("/tag/{tag_id}", response_model=TagResponse)
async def update_tag(tag_id: int, tag_data: TagCreate, db: AsyncSession = Depends(get_db)):
    """タグを更新"""
    tag = await tag_crud.get_tag_by_id(db, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    existing_tag = await tag_crud.get_tag_by_name(db, tag_data.name)
    if existing_tag and existing_tag.id != tag_id:
        raise HTTPException(status_code=400, detail="Tag with this name already exists")
    
    updated_tag = await tag_crud.update_tag(db, tag, tag_data.name)
    return updated_tag

@router.delete("/tag/{tag_id}")
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    """タグを削除"""
    tag = await tag_crud.get_tag_by_id(db, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    await tag_crud.delete_tag(db, tag)
    return {"message": "Tag deleted successfully"}