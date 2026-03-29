# -------------------------
# 🏗️ STAGE 1 — BUILDER
# -------------------------
FROM python:3.12-slim AS builder

WORKDIR /build

ARG INSTALL_VECTOR_DB=false

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --upgrade pip

RUN if [ "$INSTALL_VECTOR_DB" = "true" ]; then \
      pip wheel --no-cache-dir --wheel-dir /wheels .[vector-db]; \
    else \
      pip wheel --no-cache-dir --wheel-dir /wheels .; \
    fi

# -------------------------
# 🚀 STAGE 2 — RUNTIME
# -------------------------
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app/src

ENV STORAGE=memory
ENV APP_PROFILE=hybrid
ENV WORKERS=2

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

COPY src ./src
COPY pyproject.toml .
COPY README.md .

RUN useradd -m appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["sh", "-c", "uvicorn rpg_narrative_server.app:app --host 0.0.0.0 --port 8000 --workers ${WORKERS}"]
