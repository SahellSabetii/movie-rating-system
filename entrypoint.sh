#!/bin/sh
set -e

echo "Waiting for database..."
until pg_isready -h db -p 5432 -U "${POSTGRES_USER}"; do
  sleep 2
done
echo "Database is ready."

if [ ! "$(ls -A ./alembic/versions)" ]; then
  echo "Generating initial Alembic revision..."
  alembic revision --autogenerate -m "initial"
  alembic upgrade head
  cd scripts
  psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -h db -f seeddb.sql
  cd ..
fi

echo "Applying migrations..."
alembic upgrade head

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
