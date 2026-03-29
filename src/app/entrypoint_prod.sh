# entrypoint_reload.sh
#!/usr/bin/env bash

echo "Run Fast Api app ...."
gunicorn --bind :8000 --workers 1 --threads 1 --max-requests 1 app:app --worker-class uvicorn.workers.UvicornH11Worker --log-level=info --reload  --reload-engine 'poll'
