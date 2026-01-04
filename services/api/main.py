```python
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import httpx
import redis
import os
import hashlib
import time
from datetime import datetime

app = FastAPI(title="Armature API - The Mantle Conduit")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MEILI_URL = os.getenv("MEILI_URL", "http://meilisearch:7700")
MEILI_KEY = os.getenv("MEILI_KEY", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
WP_WEBHOOK_SECRET = os.getenv("WP_WEBHOOK_SECRET", "")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str
    sport: str
    limit: Optional[int] = 20

class ArticleRequest(BaseModel):
    topic: str
    sport: str
    length: Optional[int] = 500
    user_email: str
    site_url: str

def verify_webhook_secret(secret: str):
    if secret != WP_WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid webhook secret")

def check_rate_limit(user_id: str, action: str, max_per_hour: int = 10):
    key = f"ratelimit:{user_id}:{action}:{datetime.now().strftime('%Y%m%d%H')}"
    current = redis_client.get(key)
    if current and int(current) >= max_per_hour:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Max {max_per_hour} {action}s per hour.")
    redis_client.incr(key)
    redis_client.expire(key, 3600)

@app.get("/")
async def root():
    return {
        "status": "alive",
        "message": "Armature API - The Mantle Conduit",
        "services": {
            "ollama": OLLAMA_URL,
            "meilisearch": MEILI_URL,
            "redis": "connected" if redis_client.ping() else "disconnected"
        }
    }

@app.get("/health")
async def health_check():
    services = {}
    try:
        async with httpx.AsyncClient() as client:
            ollama_response = await client.get(f"{OLLAMA_URL}/api/tags", timeout=5.0)
            services["ollama"] = "healthy" if ollama_response.status_code == 200 else "unhealthy"
    except:
        services["ollama"] = "unreachable"
    try:
        async with httpx.AsyncClient() as client:
            meili_response = await client.get(f"{MEILI_URL}/health", timeout=5.0)
            services["meilisearch"] = "healthy" if meili_response.status_code == 200 else "unhealthy"
    except:
        services["meilisearch"] = "unreachable"
    try:
        services["redis"] = "healthy" if redis_client.ping() else "unhealthy"
    except:
        services["redis"] = "unreachable"
    all_healthy = all(status == "healthy" for status in services.values())
    return {
        "status": "healthy" if all_healthy else "degraded",
        "services": services,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/search/photos")
async def search_photos(search: SearchRequest, x_webhook_secret: str = Header(None)):
    verify_webhook_secret(x_webhook_secret)
    user_hash = hashlib.md5(search.sport.encode()).hexdigest()
    check_rate_limit(user_hash, "search", max_per_hour=100)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MEILI_URL}/indexes/photos/search",
                json={
                    "q": search.query,
                    "filter": f"sport = {search.sport}",
                    "limit": search.limit
                },
                headers={"Authorization": f"Bearer {MEILI_KEY}"},
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail="Search failed")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Search timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/article")
async def generate_article(article: ArticleRequest, x_webhook_secret: str = Header(None)):
    verify_webhook_secret(x_webhook_secret)
    user_hash = hashlib.md5(article.user_email.encode()).hexdigest()
    check_rate_limit(user_hash, "article", max_per_hour=5)
    prompt = f"""Write a {article.length}-word professional article about: {article.topic}

Context: This is for {article.sport} content on {article.site_url}

Requirements:
- Professional journalism style
- Factual and informative
- Appropriate for sports media
- Around {article.length} words

Article:"""
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False
                }
            )
            if response.status_code == 200:
                result = response.json()
                article_text = result.get("response", "")
                redis_client.setex(
                    f"article:{user_hash}:{int(time.time())}",
                    86400,
                    article_text
                )
                return {
                    "success": True,
                    "article": article_text,
                    "word_count": len(article_text.split()),
                    "generated_at": datetime.now().isoformat()
                }
            else:
                raise HTTPException(status_code=response.status_code, detail="Generation failed")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Generation timeout - article too complex")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats(x_webhook_secret: str = Header(None)):
    verify_webhook_secret(x_webhook_secret)
    try:
        searches_today = len(redis_client.keys("ratelimit:*:search:*"))
        articles_today = len(redis_client.keys("ratelimit:*:article:*"))
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "searches_today": searches_today,
            "articles_today": articles_today,
            "cost_today": 0.00,
            "status": "operational"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)