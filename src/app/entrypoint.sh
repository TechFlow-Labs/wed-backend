# entrypoint.sh
#!/usr/bin/env bash

echo "Run Fast Api app ...."
gunicorn --bind :8000 --workers 5 --threads 10 app:app --worker-class uvicorn.workers.UvicornH11Worker --log-level=info