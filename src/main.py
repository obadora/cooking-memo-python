from fastapi import FastAPI
from src.routers import recipe, tag, photo
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ReactのURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(recipe.router)
app.include_router(tag.router)
app.include_router(photo.router)