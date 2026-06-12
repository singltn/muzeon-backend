FROM python:3.13-slim

RUN apt-get update && apt-get install -y curl

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync

COPY . .

RUN useradd -m -r appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "run.py"]