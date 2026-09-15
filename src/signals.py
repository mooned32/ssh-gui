"""Typed boundaries for Qt calls that PyQt6 leaves untyped.

Accessing ``signal.connect`` or ``setHorizontalHeaderLabels`` directly is
partially unknown to the type checker, which fails strict checking. These
protocols describe the exact shape used here (parameterless slots, string
headers), so every call site stays fully typed.
"""

from collections.abc import Callable
from typing import Protocol


class Signal(Protocol):
    def connect(self, slot: Callable[[], None], /) -> object: ...


class TableHeaders(Protocol):
    def setHorizontalHeaderLabels(  # noqa: N802 -- must match the Qt API name
        self, labels: list[str], /
    ) -> None: ...


def connect_signal(signal: Signal, slot: Callable[[], None]) -> None:
    _ = signal.connect(slot)


def set_header_labels(table: TableHeaders, labels: list[str]) -> None:
    table.setHorizontalHeaderLabels(labels)
