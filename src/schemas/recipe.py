from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field



# 自作レシピ用モデル
class Recipe(BaseModel):
    id: int
    name: str
    ingredients: List[str]
    photo_url: str
    reference: str
    created_at: datetime
    update_at: datetime

class RecipeCreate(BaseModel):
    name: int
    ingredients: List[str]
    photo_url: str