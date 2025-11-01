import os
import validators
import hashlib

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from app.schemas import url_schema
from app.connection import database
from app.crud.url_crud import create_short_url, get_original_url, update_urls_data, get_admin_data, get_all_url

url_router = APIRouter()

@url_router.get("/", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def home():
    return {
        "message": "Hello World"
    }

@url_router.get("/admin", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def get_admin_details(page: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), db: Session = Depends(database.get_db)):
    data = get_all_url(db, page*limit, limit)
    if not data:
        return {
            "message": "Data not available"
        }
    return data

@url_router.post("/url_shortner", response_model=url_schema.URLResponse, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def shorten_url(payload: url_schema.URLCreate, db: Session = Depends(database.get_db), ):
    if not validators.url(payload.original_url):
        raise HTTPException(status_code=400, detail="Invalid URL")
    hash_obj = hashlib.sha256(payload.original_url.encode())
    short_code = payload.brand
    if not short_code:
        short_code = hash_obj.hexdigest()[:10].upper()
    url_obj = get_original_url(db, short_code)
    if url_obj:
        raise HTTPException(status_code=409, detail=f"Short code {short_code} already exists")
    url_obj = create_short_url(db, payload.original_url, short_code)
    BASE_URL = os.getenv("BASE_URL")
    ADMIN_URL = os.getenv("ADMIN_URL")
    return {
        "short_url": f"{BASE_URL}/{url_obj.short_code}",
        "original_url": url_obj.original_url,
        "admin_url": f"{ADMIN_URL}/{url_obj.secret_key}"
    }

@url_router.get("/{short_code}")
def redirect_to_original_url(short_code: str, db: Session = Depends(database.get_db)):
    url_obj = get_original_url(db, short_code)
    if not url_obj:
        raise HTTPException(status_code=404, detail="URL not found")
    update_urls_data(db, short_code)
    return RedirectResponse(url=url_obj.original_url)

@url_router.get("/admin/{secret_key}")
def get_admin_details(secret_key: str, db: Session = Depends(database.get_db)):
    admin_data = get_admin_data(db, secret_key)
    if not admin_data:
        raise HTTPException(status_code=404, detail="URL not found")
    BASE_URL = os.getenv("BASE_URL")
    ADMIN_URL = os.getenv("ADMIN_URL")
    return {
        "short_url": f"{BASE_URL}/{admin_data.short_code}",
        "original_url": admin_data.original_url,
        "admin_url": f"{ADMIN_URL}/{admin_data.secret_key}",
        "click_count": admin_data.click_count,
        "created_at": admin_data.created_at,
        "last_accessed_at": admin_data.last_accessed_at
    }