FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS test

COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY app ./app
COPY tests ./tests
COPY pytest.ini ./

CMD ["pytest", "-q"]

FROM base AS runtime

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

RUN useradd --create-home appuser \
    && mkdir -p /data/media \
    && chown -R appuser:appuser /app /data/media
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
