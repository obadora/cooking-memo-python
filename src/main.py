from fastapi import FastAPI
from src.routers import recipe, tag
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.include_router(recipe.router)
app.include_router(tag.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ReactのURL
    allow_methods=["*"],
    allow_headers=["*"],
)