set -e
## Source our env vars
source .env_vars

## Start our app
gunicorn app:app \
    --bind "${HOST_IP}:${HOST_PORT}" \
    --workers ${WORKERS}