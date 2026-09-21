from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.routers import auth, clothes, friends, outfits, shares, users
from app.core.config import settings
from app.core.rate_limit import limiter
from app.services.storage_service import ensure_bucket


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fail fast if we're about to run in production with insecure default configuration.
    settings.validate_for_production()
    ensure_bucket()
    yield


app = FastAPI(title="Fitfolio API", version="0.1.0", lifespan=lifespan)

# Rate limiting: register the limiter and a 429 handler for exceeded limits.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
