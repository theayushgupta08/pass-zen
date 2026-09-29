"""
PassZen Clipboard Utility — Copy to clipboard with auto-clear.

Uses pyperclip for cross-platform clipboard access. After copying a password,
schedules a clear operation after the configured timeout.
"""

import threading
from typing import Optional

import pyperclip

from src.config import DEFAULT_CLIPBOARD_CLEAR_SECONDS


class ClipboardManager:
    """
    Manages clipboard operations with auto-clear functionality.

    Copies text to the clipboard and clears it after a configurable timeout.
    If a new copy is made before the timer expires, the old timer is cancelled.
    """

    def __init__(self, clear_seconds: int = DEFAULT_CLIPBOARD_CLEAR_SECONDS):
        self._clear_seconds = clear_seconds
        self._timer: Optional[threading.Timer] = None
        self._last_copied: Optional[str] = None

    @property
    def clear_seconds(self) -> int:
        return self._clear_seconds

    @clear_seconds.setter
    def clear_seconds(self, value: int):
        self._clear_seconds = value

    def copy(self, text: str):
        """
        Copy text to the system clipboard and schedule auto-clear.

        If a previous timer is running, it is cancelled first.

        Args:
            text: The text to copy to clipboard.
        """
        # Cancel any existing timer
        self.cancel_timer()

        # Copy to clipboard
        try:
            pyperclip.copy(text)
            self._last_copied = text
        except Exception:
            # pyperclip may fail on some Linux systems without xclip/xsel
            return

        # Schedule auto-clear (0 or negative means never)
        if self._clear_seconds > 0:
            self._timer = threading.Timer(
                self._clear_seconds, self._clear_clipboard
            )
            self._timer.daemon = True
            self._timer.start()

    def _clear_clipboard(self):
        """
        Clear the clipboard if it still contains the password we copied.

        This prevents clearing user data they copied from another app
        after our password was already overwritten.
        """
        try:
            current = pyperclip.paste()
            if current == self._last_copied:
                pyperclip.copy("")
        except Exception:
            pass
        finally:
            self._last_copied = None
            self._timer = None

    def cancel_timer(self):
        """Cancel any pending auto-clear timer."""
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
