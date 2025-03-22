import threading
from typing import Any

class SharedMessagePool:
    def __init__(self):
        self.pool = {}
        self.lock = threading.Lock()  # 加入锁机制

    def add(self, key: str, value: Any):
        """将值添加到池中，使用锁来确保线程安全"""
        with self.lock:
            self.pool[key] = value

    def get(self, key: str) -> Any:
        """获取值，如果池中没有该值，则插入一个空对象并返回"""
        with self.lock:
            if key not in self.pool:
                self.pool[key] = None 
            return self.pool[key]

    def remove(self, key: str):
        """从池中删除指定的键"""
        with self.lock:
            if key in self.pool:
                del self.pool[key]

    def clear(self):
        """清空整个池"""
        with self.lock:
            self.pool.clear()

shared_message_pool = SharedMessagePool()
