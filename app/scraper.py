# app/scraper.py

import httpx
import json
import asyncio
from urllib.parse import quote
import jmespath
from langdetect import detect
from datetime import datetime
import re
import random

from app.config import HEADERS, INSTAGRAM_PROFILE_URL, INSTAGRAM_GRAPHQL_URL, POST_DOCUMENT_ID, USER_POSTS_DOCUMENT_ID

# --- PROXIES ---
proxies = [
    "http://212.60.14.146:6943",
    "http://156.237.48.221:7122",
    "http://156.237.26.78:5976",
    "http://62.164.228.15:8327",
    "http://72.1.179.38:6432"
]

proxy_auth = ("ihqqebfi", "m65ebvc3vi3w")  # Authentication

# Pick a random proxy
def get_random_proxy():
    return random.choice(proxies)

# --- CLIENT CREATION ---
async def create_client():
    proxy_url = get_random_proxy()
    client = httpx.AsyncClient(
        headers=HEADERS,
        timeout=httpx.Timeout(20.0),
        proxy=proxy_url,
        proxy_auth=proxy_auth   # <-- IMPORTANT
    )
    return client

# --- FETCH WITH RETRIES ---
async def fetch_with_retries(method: str, url: str, **kwargs):
    retries = 3
    for attempt in range(retries):
        try:
            client = await create_client()
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            if attempt < retries - 1:
                await asyncio.sleep(2)
                continue
            raise e

# --- SCRAPE USER ---
async def scrape_user(username: str):
    url = INSTAGRAM_PROFILE_URL.format(username)
    response = await fetch_with_retries("GET", url)
    return response.json()["data"]["user"]

# --- SCRAPE POST (REEL) ---
async def scrape_post(url_or_shortcode: str):
    if "http" in url_or_shortcode:
        if "/reel/" in url_or_shortcode:
            shortcode = url_or_shortcode.split("/reel/")[-1].split("/")[0]
        elif "/p/" in url_or_shortcode:
            shortcode = url_or_shortcode.split("/p/")[-1].split("/")[0]
        else:
            raise ValueError("Invalid Instagram URL format.")
    else:
        shortcode = url_or_shortcode

    variables = quote(json.dumps({
        'shortcode': shortcode,
        'fetch_tagged_user_count': None,
        'hoisted_comment_id': None,
        'hoisted_reply_id': None
    }, separators=(',', ':')))
    
    body = f"variables={variables}&doc_id={POST_DOCUMENT_ID}"
    response = await fetch_with_retries(
        "POST",
        INSTAGRAM_GRAPHQL_URL,
        headers={"content-type": "application/x-www-form-urlencoded"},
        data=body
    )
    return response.json()["data"]["xdt_shortcode_media"]

# --- SCRAPE USER POSTS ---
async def scrape_user_posts(username: str, max_pages: int = 1):
    all_posts = []
    variables = {
        "after": None,
        "before": None,
        "data": {
            "count": 12,
            "include_reel_media_seen_timestamp": True,
            "include_relationship_info": True,
            "latest_besties_reel_media": True,
            "latest_reel_media": True
        },
        "first": 12,
        "last": None,
        "username": username,
        "__relay_internal__pv__PolarisIsLoggedInrelayprovider": True,
        "__relay_internal__pv__PolarisShareSheetV3relayprovider": True
    }

    prev_cursor = None
    page_count = 0

    while page_count < max_pages:
        body = f"variables={quote(json.dumps(variables, separators=(',', ':')))}&doc_id={USER_POSTS_DOCUMENT_ID}"
        response = await fetch_with_retries(
            "POST",
            INSTAGRAM_GRAPHQL_URL,
            headers={"content-type": "application/x-www-form-urlencoded"},
            data=body
        )
        data = response.json()
        posts = data["data"]["xdt_api__v1__feed__user_timeline_graphql_connection"]["edges"]

        for post in posts:
            all_posts.append(post["node"])

        page_info = data["data"]["xdt_api__v1__feed__user_timeline_graphql_connection"]["page_info"]
        if not page_info["has_next_page"] or page_info["end_cursor"] == prev_cursor:
            break

        prev_cursor = page_info["end_cursor"]
        variables["after"] = page_info["end_cursor"]
        page_count += 1

    return all_posts

# --- GET VIDEO FILE SIZE ---
async def get_video_file_size(url: str) -> float:
    proxy_url = get_random_proxy()
    async with httpx.AsyncClient(
        headers=HEADERS,
        timeout=httpx.Timeout(20.0),
        proxy=proxy_url,
        proxy_auth=proxy_auth
    ) as client:
        response = await client.head(url)
        size_bytes = int(response.headers.get("content-length", 0))
        size_mb = size_bytes / (1024 * 1024)
        return round(size_mb, 2)

# --- LANGUAGE DETECTION ---
def safe_detect_language(text: str) -> str:
    try:
        return detect(text)
    except:
        return "unknown"

# --- PARSE REEL DATA ---
async def parse_reel(data: dict) -> dict:
    raw = jmespath.search("""
    {
        id: id,
        shortcode: shortcode,
        username: owner.username,
        caption: edge_media_to_caption.edges[0].node.text,
        video_url: video_url,
        display_url: display_url,
        like_count: edge_media_preview_like.count,
        comment_count: edge_media_to_parent_comment.count,
        is_video: is_video,
        taken_at_timestamp: taken_at_timestamp,
        view_count: video_view_count,
        video_play_count: video_play_count,
        duration: video_duration,
        audio: clips_music_attribution_info.song_name
    }
    """, data)

    upload_date = datetime.utcfromtimestamp(raw['taken_at_timestamp']).strftime('%B %d, %Y')
    caption = raw.get('caption') or ""
    language = safe_detect_language(caption)
    hashtags = re.findall(r"#(\w+)", caption)
    file_size_mb = await get_video_file_size(raw['video_url'])

    return {
        "id": raw["id"],
        "shortcode": raw["shortcode"],
        "username": raw["username"],
        "caption": caption,
        "hashtags": hashtags,
        "language": language,
        "upload_date": upload_date,
        "video_url": raw["video_url"],
        "display_url": raw["display_url"],
        "file_size_mb": file_size_mb,
        "audio_title": raw.get("audio", "Original Audio"),
        "like_count": raw["like_count"],
        "comment_count": raw["comment_count"],
        "view_count": raw["view_count"],
        "duration_seconds": raw["duration"],
    }
