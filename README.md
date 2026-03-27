# 🧠 RPG Narrative Server

![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Architecture](https://img.shields.io/badge/architecture-clean--hexagonal-orange)
![RAG](https://img.shields.io/badge/RAG-multi--stage-purple)
![Status](https://img.shields.io/badge/status-active-success)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal)
![Discord](https://img.shields.io/badge/Discord-Interactions-blue)
![Tests](https://img.shields.io/badge/tests-pytest-informational)
![Build](https://github.com/SergioLacerda/rpg-narrative-server/actions/workflows/ci.yml/badge.svg)
![Coverage](https://codecov.io/gh/SergioLacerda/rpg-narrative-server/branch/main/graph/badge.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)
---

## 🚀 Narrative Engine for RPG Storytelling

RPG Narrative Server is a **modular narrative engine** powered by:

- 🧠 LLM (OpenAI or local)
- 🔎 Advanced RAG pipeline
- 💾 Persistent campaign memory
- 🔌 Multiple interfaces (Discord, API, CLI)

> This is **not a bot** — it is a **narrative server platform**.

---

## 🌍 Documentation

### 🇧🇷 Português

- 📚 docs/pt-br/README.md
- ⚙️ docs/pt-br/setup.md
- 🧠 docs/pt-br/architecture.md
- 🔎 docs/pt-br/rag_pipeline.md
- 📊 docs/pt-br/benchmark.md

### 🇺🇸 English

- 📚 docs/en/README.md
- ⚙️ docs/en/setup.md
- 🧠 docs/en/architecture.md
- 🔎 docs/en/rag_pipeline.md
- 📊 docs/en/benchmark.md

---

## 🚀 Quick Start

```bash
git clone https://github.com/SergioLacerda/rpg-narrative-server.git
cd rpg-narrative-server

python3 -m venv .venv
source .venv/bin/activate

pip install -e .[dev,full]

cp .env.example .env

uvicorn rpg_narrative_server.app:app --reload
```

👉 Open API docs:

```bash
http://localhost:8000/docs
```

---

## 🧠 Core Concepts

### 🔹 Clean Architecture

- Domain is isolated
- UseCases define behavior
- Infrastructure is replaceable

### 🔹 RAG Pipeline

- Hybrid retrieval (vector + keyword + graph + timeline)
- Multi-stage ranking
- Context-aware generation

### 🔹 Narrative Engine

- Persistent memory
- Event-driven updates
- Multi-session campaigns

---

## 🧪 Testing

```bash
pytest --cov=src/rpgbot --cov-report=term-missing 
```

---

## 📊 Benchmark

```bash
python scripts/benchmark_retrieval.py --n 200 --mode jitter --batch --memory
```

---

## 🤝 Contributing

- Do not couple infra into domain
- Use ports for integrations
- Avoid overengineering

---

## 📌 Status

- 🚧 Active development
- 🔧 Stabilization phase
- 🧠 RAG evolving

---

## 🚀 Vision

A platform for:

- dynamic storytelling
- AI-driven RPG campaigns
- extensible narrative systems
