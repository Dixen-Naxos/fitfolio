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

`docker-compose.prod.yml` provides an override with persistent volumes suited for a self-hosted
VPS/home server deployment, and routes both the API and the web frontend through an existing
Traefik instance (run separately, in another docker-compose project on the same server) over a
shared external Docker network called `traefik`.

Set the following in a root `.env` file (see [.env.example](.env.example)) before starting:
- `API_DOMAIN_NAME` — the domain pointed at your server for the API, e.g. `api.fitfolio.example.com`
- `FRONTEND_DOMAIN_NAME` — the domain pointed at your server for the web app, e.g. `fitfolio.example.com`
- `DOCKERHUB_USERNAME` — required for the CI/CD workflows' `docker compose pull` step to resolve
  the right image tags

Make sure the external `traefik` network already exists (created by whatever compose project runs
your Traefik instance) before starting this stack:

```bash
docker network inspect traefik >/dev/null 2>&1 || docker network create traefik
```

```bash
cp .env.example .env   # fill in API_DOMAIN_NAME, FRONTEND_DOMAIN_NAME, DOCKERHUB_USERNAME
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Traefik picks up routing for the `api` and `web` services automatically via Docker labels (see
`docker-compose.prod.yml`); neither is published on any host port directly, only reachable through
Traefik. Both services use the `myresolver` certificate resolver and the `websecure` entrypoint,
matching this server's Traefik instance (TLS-ALPN challenge on 443 only, no plain-HTTP entrypoint
to redirect from). If your Traefik setup ever changes resolver/entrypoint names, update the labels
in `docker-compose.prod.yml` to match.
