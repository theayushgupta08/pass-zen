"""
PassZen Settings Manager — Persistent user preferences.

Stores non-sensitive settings (password generation rules, UI preferences,
clipboard timeout, auto-lock timeout, etc.) in a JSON file.
"""

import json
import os
from typing import Any, Optional

from src.config import (
    SETTINGS_FILE,
    DEFAULT_PASSWORD_LENGTH,
    DEFAULT_AUTO_LOCK_SECONDS,
    DEFAULT_CLIPBOARD_CLEAR_SECONDS,
    ensure_data_dir,
)


# Default settings values
DEFAULT_SETTINGS = {
    "password_length": DEFAULT_PASSWORD_LENGTH,
    "use_uppercase": True,
    "use_lowercase": True,
    "use_digits": True,
    "use_symbols": True,
    "password_visibility": "copy_only",   # "viewable" or "copy_only"
    "clipboard_clear_seconds": DEFAULT_CLIPBOARD_CLEAR_SECONDS,
    "auto_lock_seconds": DEFAULT_AUTO_LOCK_SECONDS,
}


class SettingsManager:
    """
    Manages persistent user settings.

    Settings are loaded from disk on initialization and saved on every change.
    Unknown keys from older/newer versions are preserved.
    """

    def __init__(self):
        self._settings: dict = {}
        self._load()

    def _load(self):
        """Load settings from disk, falling back to defaults."""
        ensure_data_dir()

        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                # Merge with defaults (saved values override defaults)
                self._settings = {**DEFAULT_SETTINGS, **saved}
            except (json.JSONDecodeError, Exception):
                self._settings = dict(DEFAULT_SETTINGS)
        else:
            self._settings = dict(DEFAULT_SETTINGS)

    def _save(self):
        """Persist current settings to disk."""
        ensure_data_dir()
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any):
        """Set a setting value and persist to disk."""
        self._settings[key] = value
        self._save()

    def get_all(self) -> dict:
        """Return a copy of all settings."""
        return dict(self._settings)

    def reset_to_defaults(self):
        """Reset all settings to their defaults."""
        self._settings = dict(DEFAULT_SETTINGS)
        self._save()
