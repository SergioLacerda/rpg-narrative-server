# -------------------------
# 🏗️ Builder stage
# -------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./

# instala dependências primeiro (cache forte)
RUN pip install --upgrade pip
RUN pip install --no-cache-dir .[full]

# -------------------------
# 🚀 Runtime stage
# -------------------------
FROM python:3.12-slim

WORKDIR /app

# só runtime (sem gcc)
COPY --from=builder /usr/local /usr/local

# agora copia código
COPY src ./src
COPY pyproject.toml README.md ./

ENV PYTHONPATH=/app/src
ENV APP_PROFILE=hybrid

EXPOSE 8000

CMD ["uvicorn", "rpg_narrative_server.app:app", "--host", "0.0.0.0", "--port", "8000"]