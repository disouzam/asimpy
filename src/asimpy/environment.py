"""Simulation environment."""

from dataclasses import dataclass, field
import heapq
import itertools
from typing import TYPE_CHECKING, Callable

from .timeout import _NO_TIME, Timeout

if TYPE_CHECKING:
    from .process import Process


class Environment:
    """Simulation environment."""

    def __init__(self):
        self._now = 0
        self._pending = []
        self.active_process: "Process" | None = None
        """The process currently executing, or None between events."""

    @property
    def now(self):
        """Get the current simulated time."""
        return self._now

    def immediate(self, callback):
        """Schedule a callback for immediate execution."""
        self.schedule(self._now, callback)

    def run(self, until=None):
        """Run simulation."""
        while self._pending:
            pending = heapq.heappop(self._pending)
            if until is not None and pending.time > until:
                break
            result = pending.callback()
            if (result is not _NO_TIME) and (pending.time > self._now):
                self._now = pending.time

    def schedule(self, time, callback):
        """Schedule a callback to run at a specified future time."""
        heapq.heappush(self._pending, _Pending(time, callback))

    def timeout(self, delay):
        """Create delay."""
        return Timeout(self, delay)

    def __str__(self):
        return f"Env(t={self._now})"


@dataclass(order=True)
class _Pending:
    _counter = itertools.count()

    time: float
    serial: int = field(init=False, repr=False, compare=True)
    callback: Callable = field(compare=False)

    def __post_init__(self):
        self.serial = next(self._counter)
