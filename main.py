import os
from fastapi import FastAPI
from app.models import url_model
from app.connection import database
from app.routes.url_route import url_router
from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from app.connection import database

@asynccontextmanager
async def lifespan(app: FastAPI):

    url_model.Base.metadata.create_all(bind=database.engine)
    r = redis.from_url(f"redis://{os.getenv("REDIS_HOST", "localhost")}:{int(os.getenv("REDIS_PORT", 6379))}", encoding="utf8", decode_responses=True)
    await FastAPILimiter.init(r)
    db = database.get_db()
    yield
    if r:
        await r.close()
    if db:
        db.close()

app = FastAPI(lifespan=lifespan)
app.include_router(url_router)
 