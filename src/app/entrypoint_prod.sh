# entrypoint_reload.sh
#!/usr/bin/env bash

set -e

echo "Run Fast Api app ...."

PORT="${PORT:-8000}"
TRUST_PROXY_HEADERS="${TRUST_PROXY_HEADERS:-true}"

FORWARDED_ALLOW_IPS=""
if [ "${TRUST_PROXY_HEADERS}" = "true" ]; then
  FORWARDED_ALLOW_IPS="--forwarded-allow-ips=*"
fi

gunicorn \
  --bind :"${PORT}" \
  --workers "${GUNICORN_WORKERS:-2}" \
  --threads "${GUNICORN_THREADS:-4}" \
  --max-requests "${GUNICORN_MAX_REQUESTS:-1000}" \
  app:app \
  --worker-class uvicorn.workers.UvicornH11Worker \
  --log-level=info \
  ${FORWARDED_ALLOW_IPS}
