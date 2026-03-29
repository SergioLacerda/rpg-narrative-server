import random
import time
from collections import OrderedDict
from typing import Any


class TTLCache:
    def __init__(
        self,
        ttl: int = 1200,
        max_items: int = 500,
        cleanup_probability: float = 0.05,
        cleanup_samples: int = 5,
    ):
        self.ttl = ttl
        self.max_items = max_items

        self.cleanup_probability = cleanup_probability
        self.cleanup_samples = cleanup_samples

        self._data: OrderedDict[str, dict] = OrderedDict()

    # ---------------------------------------------------------

    def _expired(self, ts: float) -> bool:
        return (time.time() - ts) > self.ttl

    # ---------------------------------------------------------
    # probabilistic cleanup
    # ---------------------------------------------------------

    def _maybe_cleanup(self):
        if random.random() > self.cleanup_probability:
            return

        keys = list(self._data.keys())

        if not keys:
            return

        samples = random.sample(keys, min(len(keys), self.cleanup_samples))

        for k in samples:
            entry = self._data.get(k)

            if entry and self._expired(entry["ts"]):
                self._data.pop(k, None)

    # ---------------------------------------------------------

    def get(self, key: str) -> Any | None:
        entry = self._data.get(key)

        if not entry:
            return None

        if self._expired(entry["ts"]):
            self._data.pop(key, None)

            return None

        self._data.move_to_end(key)

        self._maybe_cleanup()

        return entry["value"]

    # ---------------------------------------------------------

    def set(self, key: str, value: Any):
        self._data[key] = {
            "value": value,
            "ts": time.time(),
        }

        self._data.move_to_end(key)

        if len(self._data) > self.max_items:
            self._data.popitem(last=False)

        self._maybe_cleanup()

    # ---------------------------------------------------------

    def delete(self, key: str):
        self._data.pop(key, None)

    # ---------------------------------------------------------

    def clear(self):
        self._data.clear()

    # ---------------------------------------------------------

    def size(self):
        return len(self._data)

    def peek(self, key: str):
        entry = self._data.get(key)
        return entry["value"] if entry else None

    def items(self):
        """
        Itera sobre os valores válidos (não expirados).
        """
        for key, entry in list(self._data.items()):
            if self._expired(entry["ts"]):
                self._data.pop(key, None)
                continue

            yield key, entry["value"]
