# fitfolio

Fitfolio is a wardrobe & outfit organizer: store your clothes, compose outfits from them, and
optionally share items/outfits with friends. It ships as a Flutter app (iOS + Android) backed by
a FastAPI API.

## Repository layout

```
fitfolio/
  api/     FastAPI backend (PostgreSQL + MinIO for image storage)
  app/     Flutter app (iOS + Android + Web)
  docker-compose.yml   the production stack (db + minio + api + web), routed through an
                       existing Traefik instance
```

This project only ships one docker-compose setup, meant for production/self-hosted deployment.
For local iteration, run the API and Flutter app directly on your machine instead (see
[api/README.md](api/README.md) "Running locally without Docker" and [app/README.md](app/README.md)).

## Production / self-hosting

`docker-compose.yml` runs persistent, production-oriented services (`db`, `minio`, `api`, `web`)
and routes both `api` and `web` through an existing Traefik instance (run separately, in another
docker-compose project on the same server) over a shared external Docker network called `traefik`.

### First deployment

1. **DNS**: point `A`/`AAAA` records for both `API_DOMAIN_NAME` and `FRONTEND_DOMAIN_NAME` at this
   server's IP - required before Traefik can issue certificates.
2. **Clone the repo** on the server into the path the CI/CD workflows expect (`~/fitfolio`, since
   `.github/workflows/*-ci.yml`'s redeploy step does `cd fitfolio/`):
   ```bash
   git clone <this-repo-url> ~/fitfolio && cd ~/fitfolio
   ```
3. **Root `.env`** (drives Traefik labels, CORS, and which images get pulled):
   ```bash
   cp .env.example .env
   ```
   Fill in `API_DOMAIN_NAME`, `FRONTEND_DOMAIN_NAME`, `DOCKERHUB_USERNAME`. Also consider setting
   `POSTGRES_PASSWORD`/`MINIO_ROOT_PASSWORD` to something other than the defaults.
4. **`api/.env`** (the API service's own settings - `docker-compose.yml` requires this file to
   exist even if empty):
   ```bash
   cp api/.env.example api/.env
   ```
   At minimum, change `JWT_SECRET_KEY` to a real random value (`openssl rand -hex 32`) - the
   default placeholder must never be used in production, since anyone who read this repo could
   forge auth tokens with it.
5. **External Traefik network**: confirm it already exists (it should, since Traefik is already
   running from your other compose project):
   ```bash
   docker network inspect traefik
   ```
6. **First build + start** (don't rely on CI for the very first run - no image has been pushed to
   Docker Hub yet):
   ```bash
   docker compose up -d --build
   ```
7. **Run database migrations** (tables don't exist yet on a fresh Postgres volume):
   ```bash
   docker compose exec api alembic upgrade head
   ```
8. Verify: `https://<FRONTEND_DOMAIN_NAME>` loads the app, and `https://<API_DOMAIN_NAME>/health`
   returns `{"status": "ok"}`.

From then on, pushing to `main` (or manually running the workflows) builds+pushes images to Docker
Hub and redeploys automatically via SSH (`docker compose pull && up -d`) - no more manual steps
needed unless there's a new migration to run.

### Ongoing config reference

Set the following in the root `.env` file (see [.env.example](.env.example)):
- `API_DOMAIN_NAME` — the domain pointed at your server for the API, e.g. `api.fitfolio.example.com`
- `FRONTEND_DOMAIN_NAME` — the domain pointed at your server for the web app, e.g. `fitfolio.example.com`
- `DOCKERHUB_USERNAME` — required for the CI/CD workflows' `docker compose pull` step to resolve
  the right image tags

Traefik picks up routing for the `api` and `web` services automatically via Docker labels (see
`docker-compose.yml`); neither is published on any host port directly, only reachable through
Traefik. Both services use the `myresolver` certificate resolver and the `websecure` entrypoint,
matching this server's Traefik instance (TLS-ALPN challenge on 443 only, no plain-HTTP entrypoint
to redirect from). If your Traefik setup ever changes resolver/entrypoint names, update the labels
in `docker-compose.yml` to match.
