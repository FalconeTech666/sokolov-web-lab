from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
import httpx

router = APIRouter()

GNEWS_BASE_URL = "https://gnews.io/api/v4/search"
API_KEY = "ebffd11d2edb974ca19f5c260ad37fef"  

class NewsArticle(BaseModel):
    title: str = Field(..., description="Заголовок новости")
    url: str = Field(..., description="Ссылка на новость")
    source: str = Field(..., description="Источник новости")
    published_at: str = Field(..., description="Дата публикации в ISO формате")

@router.get("/search")
async def search_news(q: str, lang: str = "ru", page: int = 1, page_size: int = 10):
    """
    Поиск новостей по ключевому слову.

    Параметры:
    - q: поисковый запрос (обязателен)
    - lang: язык новостей (по умолчанию ru)
    - page: номер страницы (по умолчанию 1)
    - page_size: размер страницы (по умолчанию 10)
    """
    if page < 1:
        raise HTTPException(status_code=400, detail="page must be >= 1")
    if not (1 <= page_size <= 50):
        raise HTTPException(status_code=400, detail="page_size must be between 1 and 50")
    
    params = {
        "q": q,
        "lang": lang,
        "max": page_size,
        "page": page,
        "apikey": API_KEY,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(GNEWS_BASE_URL, params=params)
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="External news service is unavailable")

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Error from external news service")

    data = resp.json()
    raw_articles = data.get("articles", [])

    articles: List[NewsArticle] = []

    for item in raw_articles:
        article = NewsArticle(
            title=item.get("title", "No title"),
            url=item.get("url", ""),
            source=item.get("source", {}).get("name", "Unknown"),
            published_at=item.get("publishedAt", ""),
        )
        articles.append(article)

    return {
        "ok": True,
        "query": {
            "q": q,
            "lang": lang,
            "page": page,
            "page_size": page_size,
        },
        "articles": articles,
    }

