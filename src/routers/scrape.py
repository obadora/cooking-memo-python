# from fastapi import APIRouter
# from src.services.scrape import scrape_recipe
# from pydantic import BaseModel
# router = APIRouter()

# class ScrapeRequest(BaseModel):
#     url: str

# @router.post("/scrape")
# def scrape_data(request: ScrapeRequest):
#     return scrape_recipe(request.url)
