# fitfolio

Fitfolio is a wardrobe & outfit organizer: store your clothes, compose outfits from them, and
optionally share items/outfits with friends. It ships as a Flutter app (iOS + Android) backed by
a FastAPI API.

## Repository layout

```
fitfolio/
  api/     FastAPI backend (PostgreSQL + Garage for image storage)
  app/     Flutter app (iOS + Android + Web)
  docker-compose.yml   the production stack (db + garage + api + web), routed through an
                       existing Traefik instance
```

This project only ships one docker-compose setup, meant for production/self-hosted deployment.
For local iteration, run the API and Flutter app directly on your machine instead (see
[api/README.md](api/README.md) "Running locally without Docker" and [app/README.md](app/README.md)).

## Production / self-hosting

`docker-compose.yml` runs persistent, production-oriented services (`db`, `garage`, `api`, `web`)
and routes both `api` and `web` through an existing Traefik instance (run separately, in another
docker-compose project on the same server) over a shared external Docker network called `traefik`.

### First deployment

1. **DNS**: point `A`/`AAAA` records for `API_DOMAIN_NAME`, `FRONTEND_DOMAIN_NAME`, and
   `GARAGE_API_DOMAIN_NAME` at this server's IP - required before Traefik can issue certificates.
2. **Clone the repo** on the server into the path the CI/CD workflows expect (`~/fitfolio`, since
   `.github/workflows/*-ci.yml`'s redeploy step does `cd fitfolio/`):
   ```bash
   git clone <this-repo-url> ~/fitfolio && cd ~/fitfolio
   ```
3. **Root `.env`** (drives Traefik labels, CORS, and which images get pulled):
   ```bash
   cp .env.example .env
   ```
   Fill in `API_DOMAIN_NAME`, `FRONTEND_DOMAIN_NAME`, `GARAGE_API_DOMAIN_NAME`,
   `DOCKERHUB_USERNAME`. Also consider setting `POSTGRES_PASSWORD`/`GARAGE_SECRET_KEY` to
   something other than the defaults.
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
- `GARAGE_API_DOMAIN_NAME` — the domain pointed at your server for Garage's S3 API traffic (used in
   presigned upload/download URLs), e.g. `garage.fitfolio.example.com`
- `DOCKERHUB_USERNAME` — required for the CI/CD workflows' `docker compose pull` step to resolve
  the right image tags

Traefik picks up routing for the `api`, `web`, and `garage` services automatically via Docker
labels (see `docker-compose.yml`); none are published on public host ports directly, only reachable
through Traefik. All three use the `myresolver` certificate resolver and the `websecure`
entrypoint, matching this server's Traefik instance (TLS-ALPN challenge on 443 only, no
plain-HTTP entrypoint to redirect from). If your Traefik setup ever changes resolver/entrypoint
names, update the labels in `docker-compose.yml` to match.

## TODO / Roadmap

An audit of the current codebase surfaced the following gaps and improvement
opportunities. Items are grouped by area and roughly ordered by priority within
each group. This is a living list — check items off as they land.

### Security (highest priority)

- [x] **Fail-fast config validation**: reject placeholder `JWT_SECRET_KEY`,
  wildcard CORS, and default DB/Garage credentials at startup in production
  (`api/app/core/config.py`, `api/app/main.py`). Nothing currently prevents
  deploying with insecure defaults.
- [x] **Remove tracked secrets**: ensure `api/.env` is not committed (only
  `api/.env.example` should be), and move the hardcoded `rpc_secret` out of
  `garage/garage.toml`.
- [x] **Rate limiting / brute-force protection** on auth endpoints
  (`api/app/api/v1/routers/auth.py`) — currently fully exposed to credential
  stuffing.
- [ ] **Access-token revocation**: `get_current_user` does not consult
  revocation state (`api/app/api/deps.py`); only refresh-token jtis are stored.
  Add revocation checks and "log out all sessions" support.
- [ ] **File-upload hardening**: reject unknown `content_type` instead of
  silently coercing to `.jpg` (`api/app/services/storage_service.py`); verify
  object existence (HEAD), MIME type, and size before `confirm-image` accepts a
  key (`api/app/api/v1/routers/clothes.py`).
- [ ] **Stronger password policy**: registration only enforces `min_length=8`
  (`api/app/schemas/auth.py`). Add complexity/breach screening if desired.
- [ ] **Case-insensitive email uniqueness** at the DB layer
  (`api/app/models/user.py`).
- [ ] **TrustedHost / proxy hardening + request-body size limits** in
  `api/app/main.py`.
- [ ] **Client-side session hygiene**: clear cached Wardrobe/Outfits/Friends
  Cubit state and the cached `user` on logout (`app/lib/main.dart`,
  `auth_cubit.dart`, `auth_state.dart`, `friends_state.dart`); propagate
  token-refresh failure back into auth state (`app/lib/core/network/auth_interceptor.dart`).
- [ ] **Validate presigned upload URL host/scheme** on the client before PUTing
  bytes (`app/lib/features/wardrobe/data/wardrobe_repository.dart`).

### Backend features

- [ ] **Auto-revoke shares when a friendship is removed** — deleting a friendship
  currently leaves `Share` rows intact (`api/app/api/v1/routers/friends.py`,
  `shares.py`).
- [ ] **Cascade share cleanup** when a clothing item or outfit is deleted; add a
  FK / cleanup so shares don't orphan (`api/app/models/share.py`,
  `clothes.py`, `outfits.py`).
- [ ] **"List who a resource is shared with"** endpoint (`shares.py`).
- [ ] **Cancel outgoing friend request** as a first-class action; implement the
  `blocked` friendship state that currently exists only as a dead enum value
  (`api/app/models/friendship.py`).
- [ ] **Account management**: password change, password reset, email
  verification, email change, and account deletion (`auth.py`, `users.py`).
- [ ] **Image lifecycle**: delete the previous object on image replacement
  (avoid orphans) and add an image-replace endpoint (`clothes.py`).
- [ ] **Pagination / filtering / sorting** for list endpoints and
  `shared-with-me`.
- [ ] **Recipient controls**: allow hiding/rejecting content shared with you.

### Backend robustness & production readiness

- [ ] **Deep health check**: `/health` should verify DB + storage connectivity,
  not return a constant payload (`api/app/main.py`). Add an API healthcheck in
  `docker-compose.yml`.
- [ ] **Global exception handling** + structured error envelope + validation
  error formatting; wrap commits with rollback on integrity errors.
- [ ] **Don't swallow storage bucket-creation errors** at startup
  (`api/app/services/storage_service.py`).
- [ ] **Structured logging + request IDs**; add metrics/tracing (Sentry /
  OpenTelemetry).
- [ ] **Run synchronous MinIO SDK calls off the event loop** (thread pool) to
  avoid blocking async routes (`storage_service.py`).
- [ ] **Apply `garage/cors.json`** to the bucket as part of deploy — nothing
  applies it today.
- [ ] **Background cleanup** for expired revoked tokens and orphaned storage
  objects.
- [ ] **Dockerfile hardening**: non-root user, healthcheck, multi-stage build
  (`api/Dockerfile`).

### Data model

- [ ] **`updated_at` columns** on mutable tables (users, clothing_items,
  outfits, friendships, shares).
- [ ] **DB-level constraints**: `requester_id != addressee_id`, no self-share,
  symmetric friendship uniqueness, share `owner_id` consistency.
- [ ] **Controlled taxonomy / limits** for clothing subcategory and `tags` (shape,
  cardinality, length) instead of free-form JSON/string.

### Frontend features

- [ ] **Edit clothing items** — `updateClothingItem` exists in the repository but
  has no Cubit/UI path (`wardrobe_repository.dart`).
- [ ] **Edit outfits** — rename and add/remove items after creation
  (`outfit_detail_screen.dart`).
- [ ] **Tag input** when adding/editing clothing items — tags render but can't be
  entered (`add_clothing_item_screen.dart`).
- [ ] **Surface clothing-item sharing** — `shareClothingItem` exists but no UI
  uses it (`friends_repository.dart`).
- [ ] **Display shared clothing items** — `friend_shared_screen.dart` only renders
  shared outfits, ignoring `sharedWithMe.clothingItems`.
- [ ] **Fuller friend management**: remove friend, cancel outgoing request,
  sent-request list, and a friend profile view. Requests currently show
  truncated IDs instead of requester identity (`friends_screen.dart`).

### Frontend robustness & UX

- [ ] **Operation-level results**: have Cubits return success/failure for
  create/delete/share/upload instead of screens guessing from list state
  (e.g. `add_clothing_item_screen.dart` assumes the new item is `state.items.first`).
- [ ] **Surface non-load errors**: delete/add/upload/share failures update
  `errorMessage` but no screen listens for them.
- [ ] **Fix permanent-spinner risk** on `friend_shared_screen.dart` when the load
  fails; add a dedicated error state.
- [ ] **Localize hardcoded strings** (e.g. delete dialog/tooltips in
  `wardrobe_screen.dart`) and add tooltips/semantics to icon-only actions.
- [ ] **Consistent image loading/error UI** across `wardrobe_screen.dart` and
  `outfit_detail_screen.dart` (currently bare `Image.network`).
- [ ] **Success feedback** for actions like sending a friend request.
- [ ] **Lazy-load tabs** so all three tabs don't fire network loads on app entry
  (`home_shell.dart` `IndexedStack`).
- [ ] **Distinguish "offline/server-down" from "logged out"** on startup
  (`auth_cubit.dart`).

### Testing

- [ ] **Backend**: cover `PATCH /users/me`, `/health`, outfit sharing, friend
  decline/remove, unshare edge cases, invalid-object-key rejection, and storage
  failures. Consider running tests against PostgreSQL (not just SQLite) to
  exercise enum/UUID/JSON behavior.
- [ ] **Frontend**: add Cubit tests, repository/interceptor tests (token
  attach/refresh), widget tests for auth/wardrobe/outfits/friends, router
  redirect tests, and localization tests. Only `app/test/models_test.dart`
  exists today.

### Infrastructure / ops

- [ ] **Garage HA**: single-node with `replication_factor = 1` — no redundancy
  (`garage/garage.toml`).
- [ ] **Backup / retention / lifecycle policy** for Garage data volumes.
- [ ] **Migration safety** for multi-instance deploys — startup currently runs
  `alembic upgrade head` inline (`docker-compose.yml`), which can race when
  scaled.
