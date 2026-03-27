import numpy as np


def cosine_similarity(a, b) -> float:
    """
    Similaridade de cosseno robusta.

    Aceita:
    - list[float]
    - numpy array
    """

    if a is None or b is None:
        return 0.0

    a = np.array(a)
    b = np.array(b)

    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-8

    if denom == 0:
        return 0.0

    return float(np.dot(a, b) / denom)


def batch_cosine_similarity(query_vec, vectors):
    q = np.array(query_vec)
    q_norm = np.linalg.norm(q) + 1e-8

    results = []

    for v in vectors:
        v = np.array(v)
        score = np.dot(q, v) / (q_norm * (np.linalg.norm(v) + 1e-8))
        results.append(score)

    return results
