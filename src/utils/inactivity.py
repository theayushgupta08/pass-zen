"""
PassZen Inactivity Monitor — Auto-lock after configurable idle timeout.

Monitors keyboard and mouse activity within the Tkinter window. If no
activity is detected for the configured duration, triggers a lock callback.
"""

import time
from typing import Callable, Optional
import tkinter as tk

from src.config import DEFAULT_AUTO_LOCK_SECONDS


class InactivityMonitor:
    """
    Monitors user activity and triggers auto-lock after inactivity.

    Binds to Tkinter events (mouse movement, key press, button clicks)
    to detect activity. Uses `after()` for periodic checking instead of
    a background thread to stay on Tkinter's main thread.
    """

    def __init__(
        self,
        root: tk.Tk,
        on_lock: Callable,
        timeout_seconds: int = DEFAULT_AUTO_LOCK_SECONDS,
    ):
        """
        Args:
            root:            The Tkinter root window.
            on_lock:         Callback to invoke when inactivity timeout fires.
            timeout_seconds: Seconds of inactivity before auto-lock.
        """
        self._root = root
        self._on_lock = on_lock
        self._timeout = timeout_seconds
        self._last_activity = time.time()
        self._check_id: Optional[str] = None
        self._running = False
        self._remaining_callback: Optional[Callable] = None

    @property
    def timeout(self) -> int:
        return self._timeout

    @timeout.setter
    def timeout(self, value: int):
        self._timeout = value

    @property
    def remaining_seconds(self) -> int:
        """Seconds remaining before auto-lock triggers."""
        elapsed = time.time() - self._last_activity
        remaining = max(0, self._timeout - int(elapsed))
        return remaining

    def start(self):
        """Start monitoring for inactivity."""
        self._running = True
        self._last_activity = time.time()

        # Bind activity events
        self._root.bind_all("<Motion>", self._on_activity, add="+")
        self._root.bind_all("<Key>", self._on_activity, add="+")
        self._root.bind_all("<Button>", self._on_activity, add="+")
        self._root.bind_all("<MouseWheel>", self._on_activity, add="+")

        # Start periodic check
        self._schedule_check()

    def stop(self):
        """Stop monitoring (e.g., when vault is locked or app closing)."""
        self._running = False

        if self._check_id is not None:
            self._root.after_cancel(self._check_id)
            self._check_id = None

        # Unbind events
        try:
            self._root.unbind_all("<Motion>")
            self._root.unbind_all("<Key>")
            self._root.unbind_all("<Button>")
            self._root.unbind_all("<MouseWheel>")
        except Exception:
            pass

    def reset(self):
        """Reset the inactivity timer (called on user activity)."""
        self._last_activity = time.time()

    def set_remaining_callback(self, callback: Callable[[int], None]):
        """
        Set a callback that receives the remaining seconds each check cycle.
        Useful for updating a countdown display in the UI.

        Args:
            callback: Function that takes remaining seconds as int.
        """
        self._remaining_callback = callback

    def _on_activity(self, event=None):
        """Called on any user activity — resets the timer."""
        self._last_activity = time.time()

    def _schedule_check(self):
        """Schedule the next inactivity check (every 1 second)."""
        if not self._running:
            return

        elapsed = time.time() - self._last_activity

        # Notify the UI about remaining time
        if self._remaining_callback:
            remaining = max(0, self._timeout - int(elapsed))
            try:
                self._remaining_callback(remaining)
            except Exception:
                pass

        if elapsed >= self._timeout:
            # Timeout reached — trigger lock
            self._running = False
            self._on_lock()
            return

        # Check again in 1 second
        self._check_id = self._root.after(1000, self._schedule_check)
