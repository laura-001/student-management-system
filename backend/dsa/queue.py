from __future__ import annotations

from collections.abc import Iterator
from typing import Generic, TypeVar

from dsa.linked_list import LinkedList


T = TypeVar("T")


class Queue(Generic[T]):
    """FIFO queue backed by the project's singly linked list."""

    def __init__(self, values: list[T] | None = None):
        self._items = LinkedList(values)

    def enqueue(self, value: T) -> None:
        self._items.append(value)

    def dequeue(self) -> T | None:
        return self._items.pop_left()

    def peek(self) -> T | None:
        return self._items.peek_left()

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)
