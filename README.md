# Wed Backend - Coolify Deployment (Host Nginx + Coolify)

This repository includes a Coolify-ready Docker Compose stack for:
- `api` (Python FastAPI/Uvicorn)
- `postgres` (PostgreSQL 16)

This setup is designed for servers where host Nginx already owns ports `80/443`.
The API is published only on localhost and host Nginx proxies public traffic to it.

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
4. Do not attach a Coolify domain for this service.
5. Deploy.

## 3) Host Nginx routing

The API container is published to host loopback only:
- `127.0.0.1:18000 -> container:8000`

Configure host Nginx with:

```nginx
server {
    listen 80;
    server_name api.wedapp.techflowlabs.gr;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.wedapp.techflowlabs.gr;

    ssl_certificate /etc/letsencrypt/live/api.wedapp.techflowlabs.gr/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.wedapp.techflowlabs.gr/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:18000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Apply config:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

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

## Why host Nginx mode

- Keeps your existing Nginx edge setup intact.
- Avoids host port 80/443 conflicts with Coolify Traefik.
- Lets Coolify manage app containers while Nginx manages public TLS/ingress.
