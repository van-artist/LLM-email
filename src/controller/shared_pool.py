import threading
from typing import Any
class SharedMessagePool:
    def __init__(self):
        self.pool = {}
        self.lock = threading.Lock()  # 加入锁机制

    def add(self, key: str, value: Any):
        with self.lock:
            self.pool[key] = value

    def get(self, key: str) -> Any:
        with self.lock:
            return self.pool.get(key)

    def remove(self, key: str):
        with self.lock:
            if key in self.pool:
                del self.pool[key]

    def clear(self):
        with self.lock:
            self.pool.clear()

shared_message_pool = SharedMessagePool()