#!/bin/sh
set -e

host="$1"
shift

until pg_isready -h "$host" -p 5432; do
  echo "Waiting for Postgres..."
  sleep 1
done

exec "$@"
echo "Postgres is up - executing command"