from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass
class Node(Generic[T]):
    value: T
    next: Node[T] | None = None


class LinkedList(Generic[T]):
    """Singly linked list used by project DSA helpers."""

    def __init__(self, values: list[T] | None = None):
        self.head: Node[T] | None = None
        self.tail: Node[T] | None = None
        self._length = 0
        for value in values or []:
            self.append(value)

    def append(self, value: T) -> None:
        node = Node(value=value)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            assert self.tail is not None
            self.tail.next = node
            self.tail = node
        self._length += 1

    def remove(self, predicate: Callable[[T], bool]) -> T | None:
        previous: Node[T] | None = None
        current = self.head
        while current is not None:
            if predicate(current.value):
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next
                if current is self.tail:
                    self.tail = previous
                self._length -= 1
                return current.value
            previous = current
            current = current.next
        return None

    def find(self, predicate: Callable[[T], bool]) -> T | None:
        current = self.head
        while current is not None:
            if predicate(current.value):
                return current.value
            current = current.next
        return None

    def contains(self, predicate: Callable[[T], bool]) -> bool:
        return self.find(predicate) is not None

    def pop_left(self) -> T | None:
        if self.head is None:
            return None
        node = self.head
        self.head = node.next
        if self.head is None:
            self.tail = None
        self._length -= 1
        return node.value

    def peek_left(self) -> T | None:
        return self.head.value if self.head is not None else None

    def to_list(self) -> list[T]:
        return list(self)

    def __iter__(self) -> Iterator[T]:
        current = self.head
        while current is not None:
            yield current.value
            current = current.next

    def __len__(self) -> int:
        return self._length
