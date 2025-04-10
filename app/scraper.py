# app/scraper.py

import httpx
import json
import asyncio
import math
from urllib.parse import quote
import jmespath
from langdetect import detect
from datetime import datetime
import re

from app.config import HEADERS, INSTAGRAM_PROFILE_URL, INSTAGRAM_GRAPHQL_URL, POST_DOCUMENT_ID, USER_POSTS_DOCUMENT_ID

import random

# List of proxies from your Webshare account
proxies_list = [
    "http://ihqqebfi:m65ebvc3vi3w@64.137.108.3:5596",
    "http://ihqqebfi:m65ebvc3vi3w@64.137.101.31:5345",
    "http://ihqqebfi:m65ebvc3vi3w@146.103.55.91:6143",
    "http://ihqqebfi:m65ebvc3vi3w@198.37.99.112:5903",
    "http://ihqqebfi:m65ebvc3vi3w@154.29.25.184:7195",
    "http://ihqqebfi:m65ebvc3vi3w@217.198.177.161:5677",
    "http://ihqqebfi:m65ebvc3vi3w@31.56.139.91:6160",
    "http://ihqqebfi:m65ebvc3vi3w@91.124.253.231:6591",
    "http://ihqqebfi:m65ebvc3vi3w@193.161.2.249:6672",
    "http://ihqqebfi:m65ebvc3vi3w@37.44.218.222:5905",
    "http://ihqqebfi:m65ebvc3vi3w@64.137.48.126:6333",
    "http://ihqqebfi:m65ebvc3vi3w@69.58.9.142:7212",
    "http://ihqqebfi:m65ebvc3vi3w@45.67.2.246:5820",
    "http://ihqqebfi:m65ebvc3vi3w@45.151.161.219:6310",
    "http://ihqqebfi:m65ebvc3vi3w@161.123.5.227:5276",
    "http://ihqqebfi:m65ebvc3vi3w@31.57.82.232:6813",
    "http://ihqqebfi:m65ebvc3vi3w@38.225.11.157:5438",
    "http://ihqqebfi:m65ebvc3vi3w@45.43.167.105:6287",
    "http://ihqqebfi:m65ebvc3vi3w@104.239.13.86:6715",
    "http://ihqqebfi:m65ebvc3vi3w@168.199.159.4:6065",
    "http://ihqqebfi:m65ebvc3vi3w@104.222.168.209:6025",
    "http://ihqqebfi:m65ebvc3vi3w@216.173.80.68:6325",
    "http://ihqqebfi:m65ebvc3vi3w@38.225.3.104:5387",
    "http://ihqqebfi:m65ebvc3vi3w@104.252.71.156:6084",
    "http://ihqqebfi:m65ebvc3vi3w@104.253.13.195:5627",
    "http://ihqqebfi:m65ebvc3vi3w@184.174.25.40:5929",
    "http://ihqqebfi:m65ebvc3vi3w@67.227.119.23:6352",
    "http://ihqqebfi:m65ebvc3vi3w@67.227.1.236:6517",
    "http://ihqqebfi:m65ebvc3vi3w@162.220.246.158:6442",
    "http://ihqqebfi:m65ebvc3vi3w@45.138.119.165:5914",
    "http://ihqqebfi:m65ebvc3vi3w@104.168.118.246:6202",
    "http://ihqqebfi:m65ebvc3vi3w@194.116.249.20:5871",
    "http://ihqqebfi:m65ebvc3vi3w@38.170.175.32:5701",
    "http://ihqqebfi:m65ebvc3vi3w@154.29.233.2:5763",
    "http://ihqqebfi:m65ebvc3vi3w@38.170.171.86:5786",
    "http://ihqqebfi:m65ebvc3vi3w@45.131.102.5:5657",
    "http://ihqqebfi:m65ebvc3vi3w@64.137.80.118:5145",
    "http://ihqqebfi:m65ebvc3vi3w@103.76.117.121:6386",
    "http://ihqqebfi:m65ebvc3vi3w@107.181.142.233:5826",
    "http://ihqqebfi:m65ebvc3vi3w@199.180.9.163:6183",
    "http://ihqqebfi:m65ebvc3vi3w@216.74.80.218:6790",
    "http://ihqqebfi:m65ebvc3vi3w@31.59.27.49:6626",
    "http://ihqqebfi:m65ebvc3vi3w@45.38.86.225:6154",
    "http://ihqqebfi:m65ebvc3vi3w@45.39.31.72:5499",
    "http://ihqqebfi:m65ebvc3vi3w@188.215.7.225:6289",
    "http://ihqqebfi:m65ebvc3vi3w@192.3.48.130:6123",
    "http://ihqqebfi:m65ebvc3vi3w@206.206.71.44:5684",
    "http://ihqqebfi:m65ebvc3vi3w@23.27.203.133:6868",
    "http://ihqqebfi:m65ebvc3vi3w@31.59.10.54:5625",
    "http://ihqqebfi:m65ebvc3vi3w@87.239.253.180:6429",
    "http://ihqqebfi:m65ebvc3vi3w@82.23.209.150:5991",
    "http://ihqqebfi:m65ebvc3vi3w@104.249.31.7:6091",
    "http://ihqqebfi:m65ebvc3vi3w@140.99.194.213:7590",
    "http://ihqqebfi:m65ebvc3vi3w@168.199.132.199:6271",
    "http://ihqqebfi:m65ebvc3vi3w@193.36.172.7:6090",
    "http://ihqqebfi:m65ebvc3vi3w@45.39.4.38:5463",
    "http://ihqqebfi:m65ebvc3vi3w@104.143.246.13:5968",
    "http://ihqqebfi:m65ebvc3vi3w@148.135.151.132:5625",
    "http://ihqqebfi:m65ebvc3vi3w@191.96.171.38:6551",
    "http://ihqqebfi:m65ebvc3vi3w@45.43.94.72:7322",
    "http://ihqqebfi:m65ebvc3vi3w@50.114.28.42:5527",
    "http://ihqqebfi:m65ebvc3vi3w@82.21.219.127:6468",
    "http://ihqqebfi:m65ebvc3vi3w@142.111.255.170:5459",
    "http://ihqqebfi:m65ebvc3vi3w@194.5.3.168:5680",
    "http://ihqqebfi:m65ebvc3vi3w@67.227.1.216:6497",
    "http://ihqqebfi:m65ebvc3vi3w@104.239.97.253:6006",
    "http://ihqqebfi:m65ebvc3vi3w@37.44.218.131:5814",
    "http://ihqqebfi:m65ebvc3vi3w@45.41.172.186:5929",
    "http://ihqqebfi:m65ebvc3vi3w@173.239.219.86:5995",
    "http://ihqqebfi:m65ebvc3vi3w@23.26.71.123:5606",
    "http://ihqqebfi:m65ebvc3vi3w@45.41.177.59:5709",
    "http://ihqqebfi:m65ebvc3vi3w@92.113.237.254:7338",
    "http://ihqqebfi:m65ebvc3vi3w@104.239.90.244:6635",
    "http://ihqqebfi:m65ebvc3vi3w@142.111.34.54:6019",
    "http://ihqqebfi:m65ebvc3vi3w@154.29.239.88:6127",
    "http://ihqqebfi:m65ebvc3vi3w@64.137.83.114:6054",
    "http://ihqqebfi:m65ebvc3vi3w@82.23.220.138:7477",
    "http://ihqqebfi:m65ebvc3vi3w@206.232.13.192:5858",
    "http://ihqqebfi:m65ebvc3vi3w@216.173.99.112:6454",
    "http://ihqqebfi:m65ebvc3vi3w@23.95.255.159:6743",
    "http://ihqqebfi:m65ebvc3vi3w@64.137.57.115:6124",
    "http://ihqqebfi:m65ebvc3vi3w@64.137.101.225:5539",
    "http://ihqqebfi:m65ebvc3vi3w@82.22.223.151:6502",
    "http://ihqqebfi:m65ebvc3vi3w@82.22.254.254:6114",
    "http://ihqqebfi:m65ebvc3vi3w@89.116.78.236:5847",
    "http://ihqqebfi:m65ebvc3vi3w@89.213.137.152:7027",
    "http://ihqqebfi:m65ebvc3vi3w@142.111.126.4:6731",
    "http://ihqqebfi:m65ebvc3vi3w@82.24.225.28:7869",
    "http://ihqqebfi:m65ebvc3vi3w@92.249.34.153:5835",
    "http://ihqqebfi:m65ebvc3vi3w@108.165.180.100:6063",
    "http://ihqqebfi:m65ebvc3vi3w@145.223.53.173:6707",
    "http://ihqqebfi:m65ebvc3vi3w@38.154.227.24:5725",
    "http://ihqqebfi:m65ebvc3vi3w@92.113.232.159:7743",
    "http://ihqqebfi:m65ebvc3vi3w@136.0.184.59:6480",
    "http://ihqqebfi:m65ebvc3vi3w@142.111.58.41:6619",
    "http://ihqqebfi:m65ebvc3vi3w@154.95.36.193:6887",
    "http://ihqqebfi:m65ebvc3vi3w@156.243.181.192:5680",
    "http://ihqqebfi:m65ebvc3vi3w@64.137.96.117:6684",
    "http://ihqqebfi:m65ebvc3vi3w@138.128.145.114:6033",
    "http://ihqqebfi:m65ebvc3vi3w@142.111.245.44:5911"
]


# Function to pick random proxy
def get_random_proxy():
    return random.choice(proxies_list)

# Create a new HTTPX client with a random proxy
async def create_client():
    proxy = get_random_proxy()
    client = httpx.AsyncClient(
    headers=HEADERS,
    timeout=httpx.Timeout(20.0),
    proxy=proxy     # ✅ correct
)
    return client

async def fetch_with_retries(method: str, url: str, **kwargs):
    retries = 3
    for attempt in range(retries):
        try:
            client = await create_client()  # <-- create client with random proxy
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            if attempt < retries - 1:
                await asyncio.sleep(2)
                continue
            raise e

async def scrape_user(username: str):
    url = INSTAGRAM_PROFILE_URL.format(username)
    response = await fetch_with_retries("GET", url)
    return response.json()["data"]["user"]

async def scrape_post(url_or_shortcode: str):
    """Scrape single Instagram post or Reel"""
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

async def get_video_file_size(url: str) -> float:
    """Get file size of video in MB with proxy"""
    proxy = get_random_proxy()
    async with httpx.AsyncClient(
        headers=HEADERS,
        timeout=httpx.Timeout(20.0),
        proxy=proxy  # <-- Corrected here
    ) as client:
        response = await client.head(url)
        size_bytes = int(response.headers.get("content-length", 0))
        size_mb = size_bytes / (1024 * 1024)
        return round(size_mb, 2)

def safe_detect_language(text: str) -> str:
    """Detect language safely"""
    try:
        return detect(text)
    except:
        return "unknown"

async def parse_reel(data: dict) -> dict:
    """Parse Instagram Reel data with extra features"""
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
