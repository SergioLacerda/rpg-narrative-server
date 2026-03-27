import threading


class InMemoryKVStore:

    def __init__(self):
        self._data = {}
        self._lock = threading.Lock()

    def get(self, key: str):
        with self._lock:
            return self._data.get(key)

    def set(self, key: str, value):
        with self._lock:
            self._data[key] = value

    def clear(self):
        with self._lock:
            self._data.clear()