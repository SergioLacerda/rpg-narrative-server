# 🚀 Retrieval Engine Benchmark

Documentação oficial da ferramenta de benchmark do pipeline RAG.

---

## 🧠 Objetivo

Avaliar performance do sistema de retrieval em diferentes cenários:

- Latência
- Escalabilidade
- Uso de CPU
- Eficiência de cache e deduplicação

---

## ▶️ Execução Rápida

```bash
python scripts/benchmark_retrieval.py
```

---

## ⚙️ Parâmetros

```text
| Flag | Descrição |
|------|----------|
| `--n` | Número de requests (default: 50) |
| `--no-dedup` | Desativa deduplicação |
| `--mode` | Tipo de carga (`io`, `cpu`, `jitter`) |
| `--memory` | Ativa teste de memória |
| `--batch` | Ativa batching de embeddings |
```

---

## 🔥 Cenários de Teste

### 🧊 IO-bound (default)

```bash
python scripts/benchmark_retrieval.py
```

Simula latência fixa de rede.

---

### 🌐 Jitter (mundo real)

```bash
python scripts/benchmark_retrieval.py --mode jitter
```

Simula variação de latência.

---

### 🧠 CPU-bound

```bash
python scripts/benchmark_retrieval.py --mode cpu
```

Valida gargalos de CPU.

---

### 🧨 Sem deduplicação

```bash
python scripts/benchmark_retrieval.py --no-dedup
```

Mede impacto de chamadas redundantes.

---

### 📈 Stress test

```bash
python scripts/benchmark_retrieval.py --n 200
```

Alta concorrência.

---

### 🧠 Memory pressure

```bash
python scripts/benchmark_retrieval.py --memory
```

Avalia crescimento de cache.

---

### 🚀 Batching

```bash
python scripts/benchmark_retrieval.py --batch
```

Eficiência de embeddings em lote.

---

### 🔥 Cenário completo (recomendado)

```bash
python scripts/benchmark_retrieval.py --n 200 --mode jitter --batch --memory
```

Simula produção.

---

## 📊 Métricas

- **Total time** → tempo total
- **Avg latency** → latência média
- **P95 / P99** → cauda de latência
- **Index calls** → chamadas reais (dedup)
- **Speedup** → ganho por concorrência

---

## 🧠 Interpretação

```text
| Cenário | Esperado |
|--------|---------|
| IO-bound | Escala bem |
| CPU-bound | Limitado pelo GIL |
| Dedup ON | Reduz chamadas |
| Batch ON | Menor custo |
| Jitter | Aumenta P95/P99 |
```

---

## 💡 Recomendações

- Use `--mode jitter` para simular produção
- Combine `--batch` + `--memory` para cenários reais
- Use `--mode cpu` para validar paralelismo

---

## 🧩 Integração com Arquitetura

Este benchmark valida diretamente:

- RetrievalPort (Application)
- Vector Index (Infrastructure)
- Estratégias de ranking e deduplicação

---

## 📌 Boas práticas

- Rodar benchmarks isolados (sem Discord/API)
- Comparar resultados entre profiles (local/hybrid/cloud)
- Monitorar regressões ao alterar pipeline RAG
