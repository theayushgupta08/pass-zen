"""
PassZen PIN Pad — Custom 6-digit PIN input widget.

A grid of number buttons (0-9) with backspace and a row of dots showing
how many digits have been entered. Used on both the setup and login screens.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from src.ui.theme import COLORS, FONTS


class PinPad(ttk.Frame):
    """
    A 6-digit PIN input widget with a numeric keypad and dot indicators.

    Usage:
        pin_pad = PinPad(parent, on_complete=my_callback)
        pin_pad.pack()

    The `on_complete` callback is called with the 6-digit PIN string
    when all 6 digits have been entered.
    """

    PIN_LENGTH = 6

    def __init__(
        self,
        parent: tk.Widget,
        on_complete: Callable[[str], None],
        **kwargs,
    ):
        super().__init__(parent, style="TFrame", **kwargs)
        self._on_complete = on_complete
        self._digits: list[str] = []
        self._dot_labels: list[tk.Label] = []
        self._disabled = False

        self._build_ui()

        # Bind keyboard input
        self.winfo_toplevel().bind("<Key>", self._on_key_press)

    def _build_ui(self):
        """Build the PIN pad UI."""
        # ── Dot indicators ───────────────────────────────────────────
        dots_frame = ttk.Frame(self, style="TFrame")
        dots_frame.pack(pady=(0, 30))

        for i in range(self.PIN_LENGTH):
            dot = tk.Label(
                dots_frame,
                text="○",
                font=FONTS["pin_dot"],
                fg=COLORS["text_dim"],
                bg=COLORS["bg"],
                width=2,
            )
            dot.pack(side=tk.LEFT, padx=6)
            self._dot_labels.append(dot)

        # ── Number buttons ───────────────────────────────────────────
        keypad_frame = ttk.Frame(self, style="TFrame")
        keypad_frame.pack()

        # Layout: 3x3 grid for 1-9, then bottom row with backspace, 0, enter
        buttons = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["⌫", "0", ""],
        ]

        for row_idx, row in enumerate(buttons):
            for col_idx, label in enumerate(row):
                if label == "":
                    # Empty space
                    spacer = tk.Frame(
                        keypad_frame, width=80, height=70, bg=COLORS["bg"]
                    )
                    spacer.grid(
                        row=row_idx, column=col_idx, padx=5, pady=5
                    )
                    continue

                btn = tk.Button(
                    keypad_frame,
                    text=label,
                    font=FONTS["pin"] if label != "⌫" else (FONTS["heading"]),
                    width=3,
                    height=1,
                    bg=COLORS["surface"],
                    fg=COLORS["text"],
                    activebackground=COLORS["surface_hover"],
                    activeforeground=COLORS["primary"],
                    relief=tk.FLAT,
                    borderwidth=0,
                    cursor="hand2",
                    command=lambda l=label: self._on_button(l),
                )
                btn.grid(row=row_idx, column=col_idx, padx=5, pady=5)

                # Hover effects
                btn.bind("<Enter>", lambda e, b=btn: b.configure(
                    bg=COLORS["surface_hover"]
                ))
                btn.bind("<Leave>", lambda e, b=btn: b.configure(
                    bg=COLORS["surface"]
                ))

    def _on_button(self, label: str):
        """Handle a button press."""
        if self._disabled:
            return

        if label == "⌫":
            self._backspace()
        else:
            self._add_digit(label)

    def _on_key_press(self, event):
        """Handle keyboard input."""
        if self._disabled:
            return

        if event.char and event.char.isdigit():
            self._add_digit(event.char)
        elif event.keysym == "BackSpace":
            self._backspace()

    def _add_digit(self, digit: str):
        """Add a digit to the PIN."""
        if len(self._digits) >= self.PIN_LENGTH:
            return

        self._digits.append(digit)
        self._update_dots()

        if len(self._digits) == self.PIN_LENGTH:
            # Small delay so the user sees the last dot fill
            self.after(200, self._submit)

    def _backspace(self):
        """Remove the last digit."""
        if self._digits:
            self._digits.pop()
            self._update_dots()

    def _update_dots(self):
        """Update the dot indicator display."""
        for i, dot in enumerate(self._dot_labels):
            if i < len(self._digits):
                dot.configure(text="●", fg=COLORS["primary"])
            else:
                dot.configure(text="○", fg=COLORS["text_dim"])

    def _submit(self):
        """Submit the entered PIN."""
        if len(self._digits) == self.PIN_LENGTH:
            pin = "".join(self._digits)
            self._on_complete(pin)

    def clear(self):
        """Clear all entered digits."""
        self._digits.clear()
        self._update_dots()

    def disable(self):
        """Disable the PIN pad (e.g., during lockout)."""
        self._disabled = True

    def enable(self):
        """Re-enable the PIN pad."""
        self._disabled = False

    def destroy(self):
        """Clean up keyboard bindings."""
        try:
            self.winfo_toplevel().unbind("<Key>")
        except Exception:
            pass
        super().destroy()
