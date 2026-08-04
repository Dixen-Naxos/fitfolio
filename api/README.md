# Fitfolio API

FastAPI backend for the Fitfolio app: accounts, clothing items, outfits, friends and sharing,
with images stored in MinIO (S3-compatible object storage).

## Stack

- FastAPI (async) + Pydantic v2
- SQLAlchemy 2.0 (async) + Alembic migrations
- PostgreSQL
- MinIO (S3-compatible) for images, accessed via presigned upload/download URLs
- JWT auth (access + refresh tokens, refresh rotation, server-side revocation on logout)

## Running locally without Docker

The root `docker-compose.yml` is production-oriented (pulls/builds images, requires an external
Traefik network - see the root [README.md](../README.md)), so for local iteration run the API
directly instead. Requires a running PostgreSQL and MinIO (or point `DATABASE_URL`/`MINIO_*` at
existing instances - e.g. `docker run` them standalone, or point at any reachable instances).

```bash
cd api
uv venv .venv && source .venv/bin/activate   # or: python3 -m venv .venv
uv pip install -r requirements-dev.txt        # or: pip install -r requirements-dev.txt
cp .env.example .env                          # adjust values
alembic upgrade head
uvicorn app.main:app --reload
```

API available at http://localhost:8000, docs at http://localhost:8000/docs.

## Tests

Tests run against an in-memory SQLite database and a stubbed storage backend, so no external
services are required:

```bash
source .venv/bin/activate
pytest
```

## Project layout

```
app/
  main.py               FastAPI app, router registration, startup (MinIO bucket init)
  core/                 settings (config.py), password hashing + JWT (security.py)
  db/                   async engine/session (session.py), declarative base (base.py)
  models/                SQLAlchemy models (User, ClothingItem, Outfit, OutfitItem, Friendship, Share, RevokedToken)
  schemas/                Pydantic request/response models
  api/v1/routers/         auth, users, clothes, outfits, friends, shares
  services/storage_service.py   MinIO client, presigned URL generation
alembic/                 migrations
tests/                   pytest suite (httpx ASGI client + SQLite)
```

## API overview

- `POST /api/v1/auth/register`, `/login`, `/refresh`, `/logout`
- `GET/PATCH /api/v1/users/me`
- `GET/POST /api/v1/clothes`, `GET/PATCH/DELETE /api/v1/clothes/{id}`
- `POST /api/v1/clothes/{id}/image/upload-url` then `POST /api/v1/clothes/{id}/image/confirm`
  (client uploads image bytes directly to the presigned MinIO URL)
- `GET/POST /api/v1/outfits`, `GET/PATCH/DELETE /api/v1/outfits/{id}`, `PUT /api/v1/outfits/{id}/items`
- `POST /api/v1/friends/requests`, `GET /api/v1/friends/requests`, `POST .../accept`, `POST .../decline`,
  `GET /api/v1/friends`, `DELETE /api/v1/friends/{id}`
- `POST/DELETE /api/v1/clothes/{id}/share[/​{user_id}]`, `POST/DELETE /api/v1/outfits/{id}/share[/​{user_id}]`,
  `GET /api/v1/shared-with-me` — sharing is only allowed between accepted friends

## Security notes

- Passwords hashed with bcrypt; JWT secret and DB/MinIO credentials are supplied via environment
  variables (see `.env.example`) and must never be committed.
- Access tokens are short-lived; refresh tokens rotate on use and can be revoked (logout), tracked
  via a `revoked_tokens` table.
- All resource endpoints enforce ownership or explicit-share checks — see `tests/test_clothes.py`
  and `tests/test_sharing.py` for the access-control test cases.
