from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import recipe, tag, photo

origins = [
      "http://localhost:5173",
      "http://localhost:3000",
      "http://cooking-memo-frontend-20250713-cloudshell-user.s3-website-ap-northeast-1.amazonaws.com",
      "https://d3fnspeoqks5i8.cloudfront.net",
]

app = FastAPI()

app.add_middleware(
      CORSMiddleware,
      allow_origins=origins,
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
)

app.include_router(recipe.router)
app.include_router(tag.router)
app.include_router(photo.router)
