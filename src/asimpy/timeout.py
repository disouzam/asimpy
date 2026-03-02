"""Wait for a simulated time to pass."""

from typing import TYPE_CHECKING
from .event import Event
from .environment import _NO_TIME

if TYPE_CHECKING:
    from .environment import Environment


class Timeout(Event):
    """Timeout event for sleeping."""

    def __init__(self, env: "Environment", delay: float | int):
        """
        Construct timeout.

        Args:
            env: simulation environment.
            delay: how long to wait.

        Raises:
            ValueError: for invalid `delay`.
        """
        if delay < 0:
            raise ValueError(f"timeout delay must be non-negative, got {delay}")
        super().__init__(env)
        env.schedule(env.now + delay, self._fire)

    def _fire(self):
        """Handle cancellation case."""
        if self._cancelled:
            return _NO_TIME
        self.succeed()
