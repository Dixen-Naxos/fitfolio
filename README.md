# fitfolio

Fitfolio is a wardrobe & outfit organizer: store your clothes, compose outfits from them, and
optionally share items/outfits with friends. It ships as a Flutter app (iOS + Android) backed by
a FastAPI API.

## Repository layout

```
fitfolio/
  api/     FastAPI backend (PostgreSQL + MinIO for image storage)
  app/     Flutter mobile app (iOS + Android)
  docker-compose.yml       local dev stack (postgres + minio + api)
  docker-compose.prod.yml  production overrides for self-hosted deployment
```

## Local development

### 1. Start backing services + API

```bash
cp api/.env.example api/.env   # adjust secrets as needed
docker compose up --build
```

This starts:
- `db` — PostgreSQL
- `minio` — S3-compatible object storage for clothing/outfit images (console on http://localhost:9001)
- `api` — FastAPI app on http://localhost:8000 (Swagger docs at `/docs`)

Run database migrations (first time / after model changes):

```bash
docker compose exec api alembic upgrade head
```

See [api/README.md](api/README.md) for running the API outside Docker, running tests, etc.

### 2. Run the Flutter app

```bash
cd app
flutter pub get
flutter run --dart-define=API_BASE_URL=http://localhost:8000/api/v1
```

See [app/README.md](app/README.md) for more details.

## Production / self-hosting

`docker-compose.prod.yml` provides an override with persistent volumes and a Traefik reverse proxy
(automatic HTTPS via Let's Encrypt) suited for a self-hosted VPS/home server deployment.

Set the following in a root `.env` file (see [.env.example](.env.example)) before starting:
- `DOMAIN_NAME` — the domain pointed at your server, e.g. `fitfolio.example.com`
- `ACME_EMAIL` — an email address used for Let's Encrypt certificate expiry notices

```bash
cp .env.example .env   # fill in DOMAIN_NAME and ACME_EMAIL
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Traefik picks up routing for the `api` service automatically via Docker labels (see
`docker-compose.prod.yml`) and terminates TLS on ports 80/443; the API itself is not published on
any host port in production.
