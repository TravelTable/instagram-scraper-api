# app/main.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.scraper import scrape_user, scrape_post, scrape_user_posts, parse_reel

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Instagram Reels Scraper API is running 🎬"}

@app.get("/user")
async def get_user(username: str):
    try:
        user = await scrape_user(username)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user profile: {str(e)}")

@app.get("/post")
async def get_post(url: str):
    try:
        post = await scrape_post(url)
        parsed = await parse_reel(post)  # 👈 await because parse_reel is now async
        return parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Reel: {str(e)}")

@app.get("/user_posts")
async def get_user_posts(username: str, max_pages: int = 1):
    try:
        posts = await scrape_user_posts(username, max_pages)
        return {"posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user's posts: {str(e)}")

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "An unexpected error occurred. Please try again later."},
    )
