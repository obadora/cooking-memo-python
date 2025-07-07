from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Path
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import src.schemas.recipe as recipe_schema
from src.cruds import recipe as crud_recipe
from src.db import get_db
import aiofiles
import os
import uuid
from pathlib import Path as PathLib
from typing import Optional

router = APIRouter()

# 画像保存用ディレクトリ
UPLOAD_DIR = "/workspace/uploads/photos"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# ディレクトリが存在しない場合は作成
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/recipe/{recipe_id}/cooking-record/{cooking_record_id}/photo/upload", response_model=recipe_schema.RecipePhotoResponse)
async def upload_recipe_photo(
    recipe_id: int = Path(..., description="レシピID"),
    cooking_record_id: int = Path(..., description="調理記録ID"),
    file: UploadFile = File(...),
    photo_type_id: int = 3,  # デフォルトで"my_photo"
    is_primary: bool = False,
    sort_order: int = 0,
    alt_text: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """画像ファイルをアップロードしてレシピ写真を作成"""
    try:
        # ファイル検証
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_ext = PathLib(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"File type {file_ext} not allowed")
        
        # ファイルサイズチェック
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        # ユニークなファイル名を生成
        unique_filename = f"recipe_{recipe_id}_cooking_{cooking_record_id}_{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # ファイルを保存
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # DBに保存するのはファイルパスのみ
        photo_url = f"/uploads/photos/{unique_filename}"
        
        # 写真データを作成
        photo_data = recipe_schema.RecipePhotoCreate(
            photo_url=photo_url,
            photo_type_id=photo_type_id,
            is_primary=is_primary,
            sort_order=sort_order,
            alt_text=alt_text,
            file_size=len(content),
            # 画像の解像度は必要に応じて追加実装
        )
        
        created_photo = await crud_recipe.create_recipe_photo(db, recipe_id, cooking_record_id, photo_data)
        return created_photo
        
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # ファイルが作成されていた場合は削除
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        print(f"Error in upload_recipe_photo: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/uploads/photos/{filename}")
async def get_photo(filename: str):
    """保存された画像ファイルを配信"""
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)