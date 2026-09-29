"""
PassZen Configuration — Constants, paths, and platform detection.
"""

import os
import sys
import platform


# ── App Metadata ─────────────────────────────────────────────────────────────

APP_NAME = "PassZen"
APP_VERSION = "1.0.0"
APP_WINDOW_TITLE = f"🔐 {APP_NAME}"
APP_WINDOW_MIN_WIDTH = 800
APP_WINDOW_MIN_HEIGHT = 600


# ── Platform-Specific Data Directory ─────────────────────────────────────────

def get_data_dir() -> str:
    """
    Returns the platform-specific data directory for PassZen.
    - Windows:  %APPDATA%/PassZen/
    - macOS:    ~/Library/Application Support/PassZen/
    - Linux:    ~/.config/passzen/
    """
    system = platform.system()

    if system == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, APP_NAME)
    elif system == "Darwin":
        return os.path.join(
            os.path.expanduser("~"), "Library", "Application Support", APP_NAME
        )
    else:
        # Linux and other Unix-like systems
        xdg_config = os.environ.get(
            "XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config")
        )
        return os.path.join(xdg_config, APP_NAME.lower())


def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to a bundled or development resource.
    Works seamlessly in development and inside PyInstaller frozen packages.
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, relative_path)


DATA_DIR = get_data_dir()

# ── File Paths ───────────────────────────────────────────────────────────────

VAULT_META_FILE = os.path.join(DATA_DIR, "vault_meta.json")
VAULT_DB_FILE = os.path.join(DATA_DIR, "vault.db")
RECOVERY_FILE = os.path.join(DATA_DIR, "recovery.enc")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")


# ── Crypto Constants ─────────────────────────────────────────────────────────

PBKDF2_ITERATIONS = 600_000
SALT_LENGTH = 32           # bytes
AES_KEY_LENGTH = 32        # 256 bits
NONCE_LENGTH = 12          # 96 bits for AES-GCM
RECOVERY_KEY_LENGTH = 24   # characters


# ── Password Generator Defaults ──────────────────────────────────────────────

DEFAULT_PASSWORD_LENGTH = 12
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 64

CHARACTER_POOLS = {
    "uppercase": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "lowercase": "abcdefghijklmnopqrstuvwxyz",
    "digits": "0123456789",
    "symbols": "!@#$%^&*()_+-=[]{}|;:',.<>?",
}


# ── Auto-Lock & Clipboard ───────────────────────────────────────────────────

DEFAULT_AUTO_LOCK_SECONDS = 180       # 3 minutes
DEFAULT_CLIPBOARD_CLEAR_SECONDS = 30  # 30 seconds


# ── Lockout Schedule ─────────────────────────────────────────────────────────

# Maps the failed attempt count to lockout duration in seconds.
# Attempts 1-2: no lockout (not in dict).
# Attempt 3: 30s, Attempt 4: 60s, Attempt 5+: 300s.
LOCKOUT_SCHEDULE = {
    3: 30,
    4: 60,
}
LOCKOUT_MAX_SECONDS = 300  # 5 minutes for 5+ failed attempts
LOCKOUT_THRESHOLD = 3      # Start locking out after this many attempts


# ── Predefined Categories ───────────────────────────────────────────────────

PREDEFINED_CATEGORIES = [
    "Social Media",
    "Email",
    "Banking",
    "Shopping",
    "Work",
    "Entertainment",
    "Other",
]


# ── Export / Import ──────────────────────────────────────────────────────────

EXPORT_FILE_EXTENSION = ".passzen"
EXPORT_FORMAT_VERSION = 1


# ── Ensure Data Directory Exists ─────────────────────────────────────────────

def ensure_data_dir():
    """Create the data directory if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
