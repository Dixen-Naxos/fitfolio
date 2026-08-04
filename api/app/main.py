from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import auth, clothes, friends, outfits, shares, users
from app.core.config import settings
from app.services.storage_service import ensure_bucket


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_bucket()
    yield


app = FastAPI(title="Fitfolio API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_V1_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_V1_PREFIX)
app.include_router(users.router, prefix=API_V1_PREFIX)
app.include_router(clothes.router, prefix=API_V1_PREFIX)
app.include_router(outfits.router, prefix=API_V1_PREFIX)
app.include_router(friends.router, prefix=API_V1_PREFIX)
app.include_router(shares.router, prefix=API_V1_PREFIX)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
