import string
import secrets
import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.url_model import URL
from app.schemas.url_schema import URLSchema
from app.connection.redis import redis_client

def create_short_url(db: Session, original_url: str, short_code: str):
    chars = string.ascii_uppercase + string.digits
    key = "".join(secrets.choice(chars) for _ in range(10))
    secret_key = f"{short_code}_{key}"
    db_url = URL(original_url=original_url, short_code=short_code, secret_key=secret_key)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    url_data = URLSchema.model_validate(db_url)
    cache_key = f"{os.getenv('REDIS_PREFIX')}{short_code}"
    redis_client.setex(cache_key, 60, url_data.model_dump_json())
    return db_url

def get_original_url(db: Session, short_code: str):
    cache_key = f"{os.getenv('REDIS_PREFIX')}{short_code}"
    cached_data = redis_client.get(cache_key)
    print(cached_data)
    if cached_data:
        url_obj = URLSchema.model_validate_json(cached_data)
        return URL(**url_obj.model_dump())
    url_obj = db.query(URL).filter(URL.short_code == short_code).first()
    if url_obj:
        url_data = URLSchema.model_validate(url_obj)
        redis_client.setex(cache_key, 60, url_data.model_dump_json())
    return url_obj

def update_urls_data(db: Session, short_code: str):
    url_obj = db.query(URL).filter(URL.short_code == short_code).first()
    url_obj.click_count += 1
    url_obj.last_accessed_at = datetime.now()
    db.commit()
    db.refresh(url_obj)
    cache_key = f"{os.getenv('REDIS_PREFIX')}{url_obj.short_code}"
    url_data = URLSchema.model_validate(url_obj)
    redis_client.setex(cache_key, 60, url_data.model_dump_json())

def get_admin_data(db: Session, secret_key: str):
    return db.query(URL).filter(URL.secret_key == secret_key).first()

def get_all_url(db: Session, skip: int, limit: int):
    return db.query(URL).offset(skip).limit(limit).all()