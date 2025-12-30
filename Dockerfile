FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && apt-get install -y postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml ./

RUN poetry lock && poetry install --no-root

COPY app/ ./app
COPY scripts/ ./scripts/
COPY alembic/ ./alembic/
COPY alembic.ini ./
RUN mkdir -p ./alembic/versions

EXPOSE 8000

CMD ["uvicorn", "ticketer.main:app", "--host", "0.0.0.0", "--port", "8000"]
