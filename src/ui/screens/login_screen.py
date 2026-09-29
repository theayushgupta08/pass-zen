"""
PassZen Login Screen — PIN entry with progressive lockout and recovery.
"""

import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Callable

from src.ui.theme import COLORS, FONTS
from src.ui.components.pin_pad import PinPad
from src.config import LOCKOUT_SCHEDULE, LOCKOUT_MAX_SECONDS, LOCKOUT_THRESHOLD


class LoginScreen(ttk.Frame):
    """
    PIN entry screen with progressive lockout after failed attempts.

    Lockout schedule:
    - 1-2 failed: instant retry
    - 3 failed: 30s lockout
    - 4 failed: 60s lockout
    - 5+ failed: 5min lockout
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_unlock: Callable,
        vault,
        **kwargs,
    ):
        super().__init__(parent, style="TFrame", **kwargs)
        self._parent = parent
        self._on_unlock = on_unlock
        self._vault = vault
        self._failed_attempts = 0
        self._locked_until = 0  # Unix timestamp
        self._lockout_timer_id = None

        self._build_ui()

    def _clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _build_ui(self):
        """Build the login screen."""
        self._clear()

        # Center container
        container = ttk.Frame(self, style="TFrame")
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Title
        title = ttk.Label(
            container,
            text="🔐 PassZen",
            style="HeadingXL.TLabel",
        )
        title.pack(pady=(0, 8))

        subtitle = ttk.Label(
            container,
            text="Enter your 6-digit PIN to unlock",
            style="Secondary.TLabel",
        )
        subtitle.pack(pady=(0, 30))

        # Status label (shows errors / lockout countdown)
        self._status_label = ttk.Label(
            container,
            text="",
            style="Danger.TLabel",
            font=FONTS["body_sm"],
        )
        self._status_label.pack(pady=(0, 16))

        # PIN pad
        self._pin_pad = PinPad(
            container,
            on_complete=self._on_pin_entered,
        )
        self._pin_pad.pack()

        # Forgot PIN link
        forgot_btn = ttk.Button(
            container,
            text="Forgot PIN?",
            style="Ghost.TButton",
            command=self._show_recovery,
        )
        forgot_btn.pack(pady=(20, 0))

    def _on_pin_entered(self, pin: str):
        """Handle PIN submission."""
        # Check if locked out
        now = time.time()
        if now < self._locked_until:
            remaining = int(self._locked_until - now)
            self._status_label.configure(
                text=f"⏳ Locked. Try again in {remaining}s"
            )
            self._pin_pad.clear()
            return

        # Try to unlock
        if self._vault.unlock(pin):
            self._failed_attempts = 0
            self._on_unlock()
        else:
            self._failed_attempts += 1
            self._pin_pad.clear()
            self._handle_failed_attempt()

    def _handle_failed_attempt(self):
        """Handle a failed PIN attempt with progressive lockout."""
        attempts = self._failed_attempts

        if attempts < LOCKOUT_THRESHOLD:
            self._status_label.configure(
                text=f"❌ Incorrect PIN ({attempts} failed attempt{'s' if attempts > 1 else ''})"
            )
            return

        # Determine lockout duration
        lockout_seconds = LOCKOUT_SCHEDULE.get(attempts, LOCKOUT_MAX_SECONDS)
        self._locked_until = time.time() + lockout_seconds
        self._pin_pad.disable()

        # Start countdown
        self._update_lockout_countdown(lockout_seconds)

    def _update_lockout_countdown(self, remaining: int):
        """Update the lockout countdown display."""
        if remaining <= 0:
            self._pin_pad.enable()
            self._pin_pad.clear()
            self._status_label.configure(
                text=f"❌ {self._failed_attempts} failed attempts. Try again."
            )
            self._lockout_timer_id = None
            return

        minutes = remaining // 60
        seconds = remaining % 60
        if minutes > 0:
            time_str = f"{minutes}m {seconds:02d}s"
        else:
            time_str = f"{seconds}s"

        self._status_label.configure(
            text=f"🔒 Too many attempts. Locked for {time_str}"
        )

        self._lockout_timer_id = self.after(
            1000, self._update_lockout_countdown, remaining - 1
        )

    def _show_recovery(self):
        """Show the recovery flow (Forgot PIN)."""
        question = self._vault.get_security_question()
        if not question:
            messagebox.showerror(
                "No Recovery",
                "No recovery information found.",
                parent=self.winfo_toplevel(),
            )
            return

        # Ask the security question
        answer = simpledialog.askstring(
            "Recovery — Security Question",
            f"Answer this question:\n\n{question}",
            parent=self.winfo_toplevel(),
        )

        if answer is None:
            return

        # Try to recover
        recovery_key = self._vault.recover_with_answer(answer)
        if recovery_key is None:
            messagebox.showerror(
                "Wrong Answer",
                "The answer is incorrect. Cannot recover.",
                parent=self.winfo_toplevel(),
            )
            return

        # Show recovery key and prompt for new PIN
        messagebox.showinfo(
            "Recovery Key",
            f"Your recovery key is:\n\n{recovery_key}\n\n"
            f"You'll now set a new PIN.",
            parent=self.winfo_toplevel(),
        )

        # For now, we need to get the new PIN. Show a simplified reset flow.
        self._show_reset_pin(recovery_key)

    def _show_reset_pin(self, recovery_key: str):
        """Show the PIN reset flow after successful recovery."""
        self._clear()

        container = ttk.Frame(self, style="TFrame")
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        title = ttk.Label(
            container,
            text="🔑 Set New PIN",
            style="HeadingXL.TLabel",
        )
        title.pack(pady=(0, 8))

        subtitle = ttk.Label(
            container,
            text="Enter a new 6-digit PIN",
            style="Secondary.TLabel",
        )
        subtitle.pack(pady=(0, 30))

        self._reset_pin = None
        self._recovery_key = recovery_key

        pin_pad = PinPad(
            container,
            on_complete=self._on_reset_pin_entered,
        )
        pin_pad.pack()

    def _on_reset_pin_entered(self, pin: str):
        """Handle new PIN during reset."""
        if self._reset_pin is None:
            self._reset_pin = pin
            # Confirm the new PIN
            self._clear()
            container = ttk.Frame(self, style="TFrame")
            container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

            ttk.Label(
                container, text="🔑 Confirm New PIN",
                style="HeadingXL.TLabel",
            ).pack(pady=(0, 30))

            PinPad(
                container,
                on_complete=self._on_reset_pin_confirmed,
            ).pack()
        else:
            self._on_reset_pin_confirmed(pin)

    def _on_reset_pin_confirmed(self, pin: str):
        """Confirm the new PIN and reset."""
        if pin != self._reset_pin:
            messagebox.showerror(
                "PIN Mismatch",
                "PINs don't match. Starting over.",
                parent=self.winfo_toplevel(),
            )
            self._reset_pin = None
            self._show_reset_pin(self._recovery_key)
            return

        # Use the recovery key to reset the PIN
        success = self._vault.reset_pin_with_recovery_key(
            self._recovery_key,
            pin,
            "",  # Security question will need to be re-set
            "",  # Security answer placeholder
        )

        if success:
            # Re-initialize with new PIN
            self._vault.lock()
            # The vault key is now decrypted with the old key from recovery
            # Re-initialize will create new metadata
            messagebox.showinfo(
                "PIN Reset",
                "Your PIN has been reset successfully!",
                parent=self.winfo_toplevel(),
            )
            self._failed_attempts = 0
            self._build_ui()
        else:
            messagebox.showerror(
                "Reset Failed",
                "Could not reset PIN. The recovery key may be invalid.",
                parent=self.winfo_toplevel(),
            )
            self._build_ui()

    def reset(self):
        """Reset the login screen (e.g., after auto-lock)."""
        self._locked_until = 0
        if self._lockout_timer_id:
            self.after_cancel(self._lockout_timer_id)
            self._lockout_timer_id = None
        self._build_ui()

    def destroy(self):
        """Clean up timers."""
        if self._lockout_timer_id:
            self.after_cancel(self._lockout_timer_id)
        super().destroy()
