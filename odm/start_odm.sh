#!/usr/bin/env bash
#
# start_odm.sh — pulls and starts only the ODM container,
#                auto-detecting whether to use `docker-compose`
#                or `docker compose`

set -euo pipefail

# pick the right compose command
if   command -v docker-compose &>/dev/null; then
  COMPOSE="docker-compose"
elif command -v docker &>/dev/null && docker compose version &>/dev/null; then
  COMPOSE="docker compose"
else
  echo >&2 "ERROR: neither 'docker-compose' nor 'docker compose' is available."
  echo >&2 "Install Docker Compose or enable the Docker Compose plugin."
  exit 1
fi

echo "Using compose command: $COMPOSE"

echo "Pulling latest ibmcom/odm image…"
$COMPOSE pull odm

echo "Starting ODM server…"
$COMPOSE up -d odm

echo -n "Waiting for ODM to become healthy"
until [ "$($COMPOSE ps -q odm | xargs docker inspect --format '{{.State.Health.Status}}')" = "healthy" ]; do
  echo -n .
  sleep 2
done

echo
echo "✅ ODM is healthy and listening on http://localhost:9060"
