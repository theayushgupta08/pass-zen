"""
PassZen App — Main application class.

Manages screen navigation, vault lifecycle, inactivity monitoring,
and ties all components together.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

import os
import sys

from src.config import (
    APP_WINDOW_TITLE,
    APP_WINDOW_MIN_WIDTH,
    APP_WINDOW_MIN_HEIGHT,
    get_resource_path,
)
from src.ui.theme import apply_theme, COLORS
from src.crypto.vault import Vault
from src.storage.database import Database
from src.utils.clipboard import ClipboardManager
from src.utils.inactivity import InactivityMonitor
from src.utils.settings import SettingsManager
from src.models.entry import PasswordEntry

# Screens
from src.ui.screens.setup_screen import SetupScreen
from src.ui.screens.login_screen import LoginScreen
from src.ui.screens.dashboard import Dashboard
from src.ui.screens.add_entry import AddEntryScreen
from src.ui.screens.edit_entry import EditEntryScreen
from src.ui.screens.settings_screen import SettingsScreen
from src.ui.screens.export_import import ExportImportScreen


class PassZenApp:
    """
    Main application controller.

    Manages the Tkinter root window, screen navigation, and the
    lifecycle of the vault, database, clipboard, and inactivity monitor.
    """

    def __init__(self):
        # ── Tkinter Root ─────────────────────────────────────────────
        self._root = tk.Tk()
        self._root.title(APP_WINDOW_TITLE)
        self._root.minsize(APP_WINDOW_MIN_WIDTH, APP_WINDOW_MIN_HEIGHT)
        self._root.geometry("900x650")
        self._root.configure(bg=COLORS["bg"])

        # Center on screen
        self._root.update_idletasks()
        x = (self._root.winfo_screenwidth() // 2) - 450
        y = (self._root.winfo_screenheight() // 2) - 325
        self._root.geometry(f"+{x}+{y}")

        # Set window icon
        self._set_window_icon()

        # Apply theme
        apply_theme(self._root)

        # ── Core Services ────────────────────────────────────────────
        self._vault = Vault()
        self._db = Database(self._vault)
        self._settings = SettingsManager()
        self._clipboard = ClipboardManager(
            clear_seconds=self._settings.get("clipboard_clear_seconds", 30)
        )
        self._inactivity_monitor = None

        # ── Current Screen ───────────────────────────────────────────
        self._current_screen = None

        # ── Handle window close ──────────────────────────────────────
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

        # ── Start ────────────────────────────────────────────────────
        self._navigate_to_initial_screen()

    def _set_window_icon(self):
        """Set window icon safely across platforms."""
        try:
            ico_path = get_resource_path(os.path.join("assets", "icon.ico"))
            png_path = get_resource_path(os.path.join("assets", "icon.png"))
            if sys.platform.startswith("win") and os.path.exists(ico_path):
                self._root.iconbitmap(ico_path)
            elif os.path.exists(png_path):
                icon_img = tk.PhotoImage(file=png_path)
                self._root.iconphoto(True, icon_img)
        except Exception:
            pass

    def run(self):
        """Start the Tkinter main loop."""
        self._root.mainloop()

    # ── Navigation ───────────────────────────────────────────────────────

    def _clear_screen(self):
        """Remove the current screen widget."""
        if self._current_screen is not None:
            self._current_screen.destroy()
            self._current_screen = None

    def _show_screen(self, screen: tk.Widget):
        """Display a screen widget."""
        self._clear_screen()
        self._current_screen = screen
        screen.pack(fill=tk.BOTH, expand=True)

    def _navigate_to_initial_screen(self):
        """Navigate to setup or login based on vault state."""
        if Vault.is_initialized():
            self._show_login()
        else:
            self._show_setup()

    # ── Setup ────────────────────────────────────────────────────────────

    def _show_setup(self):
        """Show the first-time setup screen."""
        self._stop_inactivity_monitor()
        screen = SetupScreen(
            self._root,
            on_complete=self._on_setup_complete,
            vault=self._vault,
        )
        self._show_screen(screen)

    def _on_setup_complete(self):
        """Handle setup completion — open the database and go to dashboard."""
        self._db.connect()
        self._show_dashboard()

    # ── Login ────────────────────────────────────────────────────────────

    def _show_login(self):
        """Show the login (PIN entry) screen."""
        self._stop_inactivity_monitor()
        screen = LoginScreen(
            self._root,
            on_unlock=self._on_unlock,
            vault=self._vault,
        )
        self._show_screen(screen)

    def _on_unlock(self):
        """Handle successful vault unlock."""
        self._db.connect()
        self._show_dashboard()

    # ── Dashboard ────────────────────────────────────────────────────────

    def _show_dashboard(self):
        """Show the main dashboard."""
        screen = Dashboard(
            self._root,
            db=self._db,
            clipboard=self._clipboard,
            on_add=self._show_add_entry,
            on_edit=self._show_edit_entry,
            on_settings=self._show_settings,
            on_lock=self._lock_vault,
            on_export_import=self._show_export_import,
            settings_manager=self._settings,
        )
        self._show_screen(screen)
        self._start_inactivity_monitor()

        # Update clipboard timeout from settings
        self._clipboard.clear_seconds = self._settings.get(
            "clipboard_clear_seconds", 30
        )

    # ── Add Entry ────────────────────────────────────────────────────────

    def _show_add_entry(self):
        """Show the add entry screen."""
        categories = [c.name for c in self._db.get_all_categories()]

        screen = AddEntryScreen(
            self._root,
            on_save=self._on_entry_saved,
            on_cancel=self._show_dashboard,
            categories=categories,
            settings_manager=self._settings,
        )
        self._show_screen(screen)

    def _on_entry_saved(self, entry: PasswordEntry):
        """Handle saving a new entry."""
        self._db.add_entry(entry)

        # Check if this has a new custom category
        existing_categories = {c.name for c in self._db.get_all_categories()}
        if entry.category not in existing_categories:
            self._db.add_category(entry.category)

        self._show_dashboard()

    # ── Edit Entry ───────────────────────────────────────────────────────

    def _show_edit_entry(self, entry: PasswordEntry):
        """Show the edit entry screen."""
        categories = [c.name for c in self._db.get_all_categories()]

        screen = EditEntryScreen(
            self._root,
            entry=entry,
            on_save=self._on_entry_updated,
            on_delete=self._on_entry_deleted,
            on_cancel=self._show_dashboard,
            categories=categories,
            settings_manager=self._settings,
        )
        self._show_screen(screen)

    def _on_entry_updated(self, entry: PasswordEntry):
        """Handle updating an existing entry."""
        self._db.update_entry(entry)

        # Check for new category
        existing_categories = {c.name for c in self._db.get_all_categories()}
        if entry.category not in existing_categories:
            self._db.add_category(entry.category)

        self._show_dashboard()

    def _on_entry_deleted(self, entry_id: str):
        """Handle deleting an entry."""
        self._db.delete_entry(entry_id)
        self._show_dashboard()

    # ── Settings ─────────────────────────────────────────────────────────

    def _show_settings(self):
        """Show the settings screen."""
        screen = SettingsScreen(
            self._root,
            settings=self._settings,
            on_back=self._show_dashboard,
            on_change_pin=self._change_pin,
            db=self._db,
        )
        self._show_screen(screen)

    def _change_pin(self):
        """Handle PIN change request."""
        # Verify current PIN first
        current_pin = simpledialog.askstring(
            "Verify PIN",
            "Enter your current 6-digit PIN:",
            show="●",
            parent=self._root,
        )

        if current_pin is None:
            return

        # Verify
        from src.crypto.key_derivation import derive_key
        import base64, json
        from src.config import VAULT_META_FILE, NONCE_LENGTH
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        try:
            with open(VAULT_META_FILE, "r") as f:
                meta = json.load(f)
            salt = base64.b64decode(meta["salt"])
            verification_token = base64.b64decode(meta["verification_token"])

            candidate_key = derive_key(current_pin, salt)
            candidate_aesgcm = AESGCM(candidate_key)

            nonce = verification_token[:NONCE_LENGTH]
            ciphertext = verification_token[NONCE_LENGTH:]
            result = candidate_aesgcm.decrypt(nonce, ciphertext, None)

            if result != b"PASSZEN_VAULT_VERIFICATION":
                raise ValueError("Wrong PIN")

        except Exception:
            messagebox.showerror(
                "Wrong PIN",
                "The current PIN is incorrect.",
                parent=self._root,
            )
            return

        # Get new PIN
        new_pin = simpledialog.askstring(
            "New PIN",
            "Enter your new 6-digit PIN:",
            show="●",
            parent=self._root,
        )
        if new_pin is None or len(new_pin) != 6 or not new_pin.isdigit():
            messagebox.showerror(
                "Invalid PIN",
                "PIN must be exactly 6 digits.",
                parent=self._root,
            )
            return

        # Confirm
        confirm_pin = simpledialog.askstring(
            "Confirm PIN",
            "Confirm your new 6-digit PIN:",
            show="●",
            parent=self._root,
        )
        if confirm_pin != new_pin:
            messagebox.showerror(
                "Mismatch",
                "PINs don't match.",
                parent=self._root,
            )
            return

        # Re-encrypt vault
        try:
            # Create new vault with new PIN
            from src.crypto.key_derivation import generate_salt

            new_salt = generate_salt()
            new_key = derive_key(new_pin, new_salt)
            new_vault = Vault()
            new_vault._key = new_key
            new_vault._salt = new_salt
            new_vault._aesgcm = AESGCM(new_key)

            # Re-encrypt all entries
            self._db.re_encrypt_all_entries(self._vault, new_vault)

            # Create new verification token
            new_verification = new_vault.encrypt(b"PASSZEN_VAULT_VERIFICATION")

            # Update metadata
            meta["salt"] = base64.b64encode(new_salt).decode("utf-8")
            meta["verification_token"] = base64.b64encode(
                new_verification
            ).decode("utf-8")

            with open(VAULT_META_FILE, "w") as f:
                json.dump(meta, f, indent=2)

            # Switch to new vault
            self._vault._key = new_key
            self._vault._salt = new_salt
            self._vault._aesgcm = AESGCM(new_key)

            messagebox.showinfo(
                "PIN Changed",
                "Your PIN has been changed successfully!",
                parent=self._root,
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Could not change PIN: {e}",
                parent=self._root,
            )

    # ── Export / Import ──────────────────────────────────────────────────

    def _show_export_import(self):
        """Show the export/import screen."""
        screen = ExportImportScreen(
            self._root,
            db=self._db,
            vault=self._vault,
            on_back=self._show_dashboard,
        )
        self._show_screen(screen)

    # ── Lock / Unlock ────────────────────────────────────────────────────

    def _lock_vault(self):
        """Lock the vault and return to login screen."""
        self._stop_inactivity_monitor()
        self._vault.lock()
        self._db.close()
        self._clipboard.cancel_timer()
        self._show_login()

    # ── Inactivity Monitor ───────────────────────────────────────────────

    def _start_inactivity_monitor(self):
        """Start the inactivity monitor for auto-lock."""
        timeout = self._settings.get("auto_lock_seconds", 180)
        if timeout <= 0:
            return  # Auto-lock disabled

        self._inactivity_monitor = InactivityMonitor(
            self._root,
            on_lock=self._lock_vault,
            timeout_seconds=timeout,
        )

        # Connect the timer display to the dashboard
        if isinstance(self._current_screen, Dashboard):
            self._inactivity_monitor.set_remaining_callback(
                self._current_screen.update_timer_display
            )

        self._inactivity_monitor.start()

    def _stop_inactivity_monitor(self):
        """Stop the inactivity monitor."""
        if self._inactivity_monitor:
            self._inactivity_monitor.stop()
            self._inactivity_monitor = None

    # ── Cleanup ──────────────────────────────────────────────────────────

    def _on_close(self):
        """Handle application close."""
        self._stop_inactivity_monitor()
        self._vault.lock()
        self._db.close()
        self._clipboard.cancel_timer()
        self._root.destroy()
