from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from src.db import Base
from sqlalchemy import Table, Text, Date, DateTime, func

# 多対多リレーションのための関連テーブル
recipe_categories_table = Table(
    'recipe_categories',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True),
)

recipe_tags_table = Table(
    'recipe_tags',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True),
)
class SourceType(Base):
    __tablename__ = "source_types"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    recipes = relationship("Recipe", back_populates="source_type")
class PhotoType(Base):
    __tablename__ = "photo_types"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    is_reference = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    photos = relationship("RecipePhoto", back_populates="photo_type") 

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    color = Column(String(7), default="#CCCCCC")
    created_at = Column(DateTime, default=func.now())
    
    recipes = relationship("Recipe", secondary=recipe_categories_table, back_populates="categories")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    
    recipes = relationship("Recipe", secondary=recipe_tags_table, back_populates="tags")

class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    cook_time = Column(Integer)
    servings = Column(Integer)
    source_type_id = Column(Integer, ForeignKey("source_types.id"), nullable=False)
    source_url = Column(String(500))
    source_recipe_id = Column(String(50))
    source_book_title = Column(String(255))
    source_page = Column(Integer)
    manual_identifier = Column(String(100))
    cooking_date = Column(Date, index=True)
    cooking_memo = Column(Text)
    rating = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    # リレーション
    source_type = relationship("SourceType", back_populates="recipes")
    photos = relationship("RecipePhoto", back_populates="recipe", cascade="all, delete-orphan")
    ingredients = relationship("Ingredient", back_populates="recipe", cascade="all, delete-orphan")
    steps = relationship("Step", back_populates="recipe", cascade="all, delete-orphan")
    categories = relationship("Category", secondary=recipe_categories_table, back_populates="recipes")
    tags = relationship("Tag", secondary=recipe_tags_table, back_populates="recipes")
class RecipePhoto(Base):
    __tablename__ = "recipe_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    photo_url = Column(String(500), nullable=False)
    photo_type_id = Column(Integer, ForeignKey("photo_types.id"), nullable=False)
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    alt_text = Column(String(255))
    file_size = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    
    recipe = relationship("Recipe", back_populates="photos")
    photo_type = relationship("PhotoType", back_populates="photos")

class Ingredient(Base):
    __tablename__ = "ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    quantity = Column(String(50))
    unit = Column(String(20))
    sort_order = Column(Integer, default=0)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    recipe = relationship("Recipe", back_populates="ingredients")

class Step(Base):
    __tablename__ = "steps"
    
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    instruction = Column(Text, nullable=False)
    time_estimate = Column(Integer)
    temperature = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    recipe = relationship("Recipe", back_populates="steps")    