from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from dsa.linked_list import LinkedList


K = TypeVar("K")
V = TypeVar("V")


@dataclass
class HashEntry(Generic[K, V]):
    key: K
    value: V


class HashTable(Generic[K, V]):
    """Hash table with separate chaining through the project's linked list."""

    def __init__(self, capacity: int = 16):
        if capacity <= 0:
            raise ValueError("capacity must be greater than zero")
        self._buckets: list[LinkedList[HashEntry[K, V]]] = [LinkedList() for _ in range(capacity)]
        self._length = 0

    def _bucket(self, key: K) -> LinkedList[HashEntry[K, V]]:
        return self._buckets[hash(key) % len(self._buckets)]

    def set(self, key: K, value: V) -> None:
        bucket = self._bucket(key)
        entry = bucket.find(lambda item: item.key == key)
        if entry is not None:
            entry.value = value
            return
        bucket.append(HashEntry(key=key, value=value))
        self._length += 1

    def get(self, key: K, default: V | None = None) -> V | None:
        entry = self._bucket(key).find(lambda item: item.key == key)
        return entry.value if entry is not None else default

    def delete(self, key: K) -> V | None:
        removed = self._bucket(key).remove(lambda item: item.key == key)
        if removed is None:
            return None
        self._length -= 1
        return removed.value

    def contains(self, key: K) -> bool:
        return self._bucket(key).contains(lambda item: item.key == key)

    def keys(self) -> list[K]:
        return [entry.key for bucket in self._buckets for entry in bucket]

    def values(self) -> list[V]:
        return [entry.value for bucket in self._buckets for entry in bucket]

    def items(self) -> list[tuple[K, V]]:
        return [(entry.key, entry.value) for bucket in self._buckets for entry in bucket]

    def __len__(self) -> int:
        return self._length










