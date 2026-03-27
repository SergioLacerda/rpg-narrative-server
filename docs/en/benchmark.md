# 🚀 Retrieval Engine Benchmark (EN)

Official documentation for the RAG retrieval benchmark tool.

---

## 🧠 Purpose

Evaluate retrieval system performance under different scenarios:

- Latency
- Scalability
- CPU usage
- Cache and deduplication efficiency

---

## ▶️ Quick Start

```bash
python scripts/benchmark_retrieval.py
```

---

## ⚙️ Parameters

```text
| Flag | Description |
|------|------------|
| `--n` | Number of requests (default: 50) |
| `--no-dedup` | Disable deduplication |
| `--mode` | Load type (`io`, `cpu`, `jitter`) |
| `--memory` | Enable memory pressure test |
| `--batch` | Enable embedding batching |
```

---

## 🔥 Test Scenarios

### 🧊 IO-bound (default)

```bash
python scripts/benchmark_retrieval.py
```

Simulates fixed network latency.

---

### 🌐 Jitter (real-world)

```bash
python scripts/benchmark_retrieval.py --mode jitter
```

Simulates variable latency.

---

### 🧠 CPU-bound

```bash
python scripts/benchmark_retrieval.py --mode cpu
```

Validates CPU bottlenecks.

---

### 🧨 No deduplication

```bash
python scripts/benchmark_retrieval.py --no-dedup
```

Measures impact of redundant calls.

---

### 📈 Stress test

```bash
python scripts/benchmark_retrieval.py --n 200
```

High concurrency scenario.

---

### 🧠 Memory pressure

```bash
python scripts/benchmark_retrieval.py --memory
```

Evaluates cache growth.

---

### 🚀 Batching

```bash
python scripts/benchmark_retrieval.py --batch
```

Tests embedding batching efficiency.

---

### 🔥 Full scenario (recommended)

```bash
python scripts/benchmark_retrieval.py --n 200 --mode jitter --batch --memory
```

Simulates production-like conditions.

---

## 📊 Metrics

- **Total time** → total execution time  
- **Avg latency** → average latency  
- **P95 / P99** → latency tail  
- **Index calls** → actual executions (dedup effect)  
- **Speedup** → concurrency gain  

---

## 🧠 Interpretation

```text

| Scenario | Expected Behavior |
|----------|------------------|
| IO-bound | Scales well |
| CPU-bound | Limited by GIL |
| Dedup ON | Reduces real calls |
| Batch ON | Reduces embedding cost |
| Jitter | Increases P95/P99 |
```

---

## 💡 Recommendations

- Use `--mode jitter` to simulate production  
- Combine `--batch` + `--memory` for realistic scenarios  
- Use `--mode cpu` to validate parallelism  

---

## 🧩 Architecture Integration

This benchmark directly validates:

- RetrievalPort (Application layer)
- Vector Index (Infrastructure)
- Ranking and deduplication strategies

---

## 📌 Best Practices

- Run benchmarks in isolation (no Discord/API running)
- Compare results across profiles (local / hybrid / cloud)
- Monitor regressions when modifying the RAG pipeline

---

## 🚀 Summary

This tool is essential to ensure:

- consistent performance
- scalability under load
- reliability of the retrieval layer

It should be used continuously during development and optimization.
