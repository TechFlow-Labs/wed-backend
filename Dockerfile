FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN set -eux; \
    if [ -f src/app/requirements.txt ]; then pip install --no-cache-dir -r src/app/requirements.txt; \
    elif [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; \
    elif [ -f requirements-prod.txt ]; then pip install --no-cache-dir -r requirements-prod.txt; \
    elif [ -f pyproject.toml ]; then \
      pip install --no-cache-dir "uvicorn[standard]" fastapi && pip install --no-cache-dir .; \
    else \
      pip install --no-cache-dir "uvicorn[standard]" fastapi; \
    fi

ENV PYTHONPATH=/app/src/app \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    APP_MODULE=app:app

EXPOSE 8000

CMD ["sh", "-c", "cd /app/src/app && uvicorn ${APP_MODULE} --host ${API_HOST} --port ${API_PORT}"]
