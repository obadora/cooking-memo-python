from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field



# 自作レシピ用モデル
# class Recipe(BaseModel):
#     id: int
#     name: str
#     ingredients: List[str]
#     photo_url: str
#     reference: str
#     created_at: datetime
#     update_at: datetime
# ベーススキーマ
class SourceTypeBase(BaseModel):
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=50)
    description: Optional[str] = None
    is_active: bool = True
    class Config:
        from_attributes = True 

class SourceType(SourceTypeBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class SourceTypeUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=20)
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    class Config:
        from_attributes = True 

class SourceTypeResponse(SourceTypeBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PhotoTypeBase(BaseModel):
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=50)
    description: Optional[str] = None
    is_reference: bool = False
    is_active: bool = True
    class Config:
        from_attributes = True 

class PhotoType(PhotoTypeBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PhotoTypeResponse(PhotoTypeBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    color: str = Field("#CCCCCC", max_length=7)
    class Config:
        from_attributes = True 

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TagBase(BaseModel):
    name: str = Field(..., max_length=50)
    class Config:
        from_attributes = True 

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class IngredientBase(BaseModel):
    name: str = Field(..., max_length=255)
    quantity: Optional[str] = Field(None, max_length=50)
    unit: Optional[str] = Field(None, max_length=20)
    sort_order: int = 0
    notes: Optional[str] = None
    class Config:
        from_attributes = True 

class IngredientCreate(IngredientBase):
    pass

class IngredientResponse(IngredientBase):
    id: int
    recipe_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class StepBase(BaseModel):
    step_number: int
    instruction: str
    time_estimate: Optional[int] = None
    temperature: Optional[int] = None
    notes: Optional[str] = None
    class Config:
        from_attributes = True 

class StepCreate(StepBase):
    pass

class StepResponse(StepBase):
    id: int
    recipe_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class RecipePhotoBase(BaseModel):
    photo_url: str = Field(..., max_length=500)
    photo_type_id: int
    is_primary: bool = False
    sort_order: int = 0
    alt_text: Optional[str] = Field(None, max_length=255)
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    class Config:
        from_attributes = True 

class RecipePhotoCreate(RecipePhotoBase):
    pass

class RecipePhotoResponse(RecipePhotoBase):
    id: int
    recipe_id: int
    photo_type: PhotoTypeResponse
    created_at: datetime
    
    class Config:
        from_attributes = True

class RecipeBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    cook_time: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    source_type_id: int
    source_url: Optional[str] = Field(None, max_length=500)
    source_recipe_id: Optional[str] = Field(None, max_length=50)
    source_book_title: Optional[str] = Field(None, max_length=255)
    source_page: Optional[int] = Field(None, ge=1)
    manual_identifier: Optional[str] = Field(None, max_length=100)
    cooking_date: Optional[date] = None
    cooking_memo: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    class Config:
        from_attributes = True 

class RecipeResponse(RecipeBase):
    id: int
    source_type: SourceTypeResponse
    ingredients: List[IngredientResponse] = []
    steps: List[StepResponse] = []
    photos: List[RecipePhotoResponse] = []
    categories: List[CategoryResponse] = []
    tags: List[TagResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RecipeListResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    cook_time: Optional[int]
    servings: Optional[int]
    rating: Optional[int]
    cooking_date: Optional[date]
    source_type: SourceTypeResponse
    categories: List[CategoryResponse] = []
    tags: List[TagResponse] = []
    primary_photo: Optional[RecipePhotoResponse] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class RecipeCreate(BaseModel):
    name: int
    ingredients: List[str]
    photo_url: str
    class Config:
        from_attributes = True 

# 基本的なレシピレスポンス（関連データなし）
class RecipeBasicResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    cook_time: Optional[int] = None
    servings: Optional[int] = None
    source_type_id: Optional[int] = None
    source_url: Optional[str] = None
    source_recipe_id: Optional[str] = None
    source_book_title: Optional[str] = None
    source_page: Optional[int] = None
    manual_identifier: Optional[str] = None
    cooking_date: Optional[datetime] = None
    cooking_memo: Optional[str] = None
    rating: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Pydantic v2では orm_mode の代わり

# 材料の基本スキーマ
class IngredientResponse(BaseModel):
    id: int
    name: str
    quantity: Optional[str] = None
    unit: Optional[str] = None
    sort_order: Optional[int] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# ステップの基本スキーマ  
class StepResponse(BaseModel):
    id: int
    step_number: int
    instruction: str
    time_estimate: Optional[int] = None
    temperature: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# 完全なレシピレスポンス（段階的に追加）
class RecipeWithIngredientsResponse(RecipeBasicResponse):
    ingredients: List[IngredientResponse] = []
    steps: List[StepResponse] = []

    class Config:
        from_attributes = True

class ScrapedRecipeData(BaseModel):
    """スクレイピングで取得したレシピデータ"""
    title: str
    description: Optional[str] = None
    source_url: str
    ingredients: List[dict] = []
    steps: List[dict] = []
    photos: List[dict] = []