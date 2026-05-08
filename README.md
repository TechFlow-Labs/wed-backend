# Wed Backend - Coolify Deployment (Traefik-only)

This repository includes a Coolify-ready Docker Compose stack for:
- `api` (Python FastAPI/Uvicorn)
- `postgres` (PostgreSQL 16)

No Nginx layer is used. Coolify already manages ingress/TLS through Traefik.

## Files

- `Dockerfile`: Production image for the API service.
- `docker-compose.coolify.yml`: Main stack for Coolify.
- `.env.coolify.example`: API/app environment template.
- `.env.db.coolify.example`: Postgres environment template.

## 1) Prepare environment files

Create real env files from templates:

```bash
cp .env.coolify.example .env.coolify
cp .env.db.coolify.example .env.db.coolify
```

Update at minimum:
- `APP_DOMAIN`
- `JWT_SECRET_KEY`
- `JWT_REFRESH_SECRET_KEY`
- `POSTGRES_PASSWORD`
- `DB_PASSWORD` (must match `POSTGRES_PASSWORD`)
- `APP_MODULE` (if your FastAPI app is not at `app:app`)

## 2) Create service in Coolify

1. Create a new **Docker Compose** service from this repo.
2. Set compose file to `docker-compose.coolify.yml`.
3. Add/confirm env files or equivalent key-value variables in Coolify.
4. Attach a domain matching `APP_DOMAIN`.
5. Deploy.

## 3) Domain and Traefik routing

Traefik labels are defined on the `api` service:
- Router rule: `Host(${APP_DOMAIN})`
- EntryPoint: `websecure`
- TLS: enabled
- Upstream port: `${API_PORT}` (default `8000`)

This is enough for Coolify-managed HTTPS routing without Nginx.

## 4) Validation

Validate compose locally:

```bash
docker compose --env-file .env.coolify --env-file .env.db.coolify -f docker-compose.coolify.yml config
```

Optional local smoke test:

```bash
docker compose --env-file .env.coolify --env-file .env.db.coolify -f docker-compose.coolify.yml up -d --build
docker compose -f docker-compose.coolify.yml ps
docker compose -f docker-compose.coolify.yml logs api --tail=100
```

## Why Traefik-only

- Coolify already integrates with Traefik for ingress and TLS.
- Removing Nginx avoids duplicate proxy configuration and an extra network hop.
- Fewer moving parts means simpler operations and easier debugging on a self-hosted VPS.
