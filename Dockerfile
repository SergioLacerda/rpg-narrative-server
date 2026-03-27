# -------------------------
# 🏗️ STAGE 1 — BUILDER
# -------------------------
FROM python:3.12-slim AS builder

WORKDIR /build

# Toolchain apenas no build
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia dependências primeiro (cache eficiente)
COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --upgrade pip

# 🔥 Build de wheels (rápido + cacheável)
RUN pip wheel --no-cache-dir --wheel-dir /wheels .[vector-db]

# -------------------------
# 🚀 STAGE 2 — RUNTIME
# -------------------------
FROM python:3.12-slim

WORKDIR /app

# 🔒 Variáveis recomendadas
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app/src
ENV APP_PROFILE=hybrid

# 📦 Copia wheels e instala
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# 📁 Copia código da aplicação
COPY . .

# 🔐 Usuário não-root (segurança)
RUN useradd -m appuser
USER appuser

# 🌐 Porta
EXPOSE 8000

# ❤️ Healthcheck (importante pra orquestradores)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# 🚀 Start da aplicação
CMD ["uvicorn", "rpg_narrative_server.app:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2"]