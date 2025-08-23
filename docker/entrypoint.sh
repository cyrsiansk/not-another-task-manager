#!/bin/sh
set -eu

echo "==> Database ready — running migrations (alembic -> migrations/)..."
PYTHONPATH=$(pwd) alembic upgrade head
echo "==> Migrations applied — starting application"
exec "$@"
