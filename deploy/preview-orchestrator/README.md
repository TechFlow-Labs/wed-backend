# Coolify Preview Orchestrator

Central HTTP service that receives PR events from all three repositories and manages a unified Coolify preview environment keyed by branch name.

## Endpoint

- `POST /preview-events`
- Auth: `Authorization: Bearer <PREVIEW_ORCHESTRATOR_TOKEN>` (required only if token is configured)

Payload format matches:
- `docs/coolify-preview-orchestrator-contract.md`

## What it does

For `action=deploy`:
1. Sanitizes `preview_key`
2. Creates or updates 3 Coolify applications (backend/main/ssr) named with the preview key
3. Sets integration env vars:
   - `backend`: DB/auth runtime env vars from `ORCH_BACKEND_*` orchestrator envs
   - `main`: `EXPO_PUBLIC_API_URL=https://api-<key>.<preview-base-domain>`
   - `ssr`: `NEXT_PUBLIC_API_URL=https://api-<key>.<preview-base-domain>`
   - `ssr`: `API_INTERNAL_URL=http://wed-preview-backend-<key>:8000`
4. Triggers deployment for each application

For `action=teardown`:
1. Finds the 3 preview applications by deterministic names
2. Deletes them from Coolify

## Required environment variables

See `.env.example`.

Important:
- `COOLIFY_PROJECT_UUID` and `COOLIFY_DESTINATION_UUID` must point to the target project/server destination.
- `PREVIEW_BASE_DOMAIN` should have a wildcard DNS record: `*.preview-base-domain` -> Coolify server.

## Run locally

```bash
cd deploy/preview-orchestrator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
set -a; source .env.example; set +a
uvicorn app:app --host 0.0.0.0 --port 8080
```

Health check:

```bash
curl http://localhost:8080/healthz
```

## Coolify API endpoints used

- `GET /api/v1/applications`
- `POST /api/v1/applications/public`
- `PATCH /api/v1/applications/{uuid}`
- `PATCH /api/v1/applications/{uuid}/envs`
- `GET /api/v1/applications/{uuid}/start`
- `DELETE /api/v1/applications/{uuid}`

These endpoints follow Coolify API reference pages for Applications.
