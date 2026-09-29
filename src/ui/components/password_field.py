"""
PassZen Password Field — Show/hide toggle password entry widget.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from src.ui.theme import COLORS, FONTS


class PasswordField(ttk.Frame):
    """
    A password entry field with a show/hide toggle button.

    The password is masked by default (shows ●●●●) and can be toggled
    to show the actual text.
    """

    def __init__(
        self,
        parent: tk.Widget,
        show_toggle: bool = True,
        font: Optional[tuple] = None,
        **kwargs,
    ):
        super().__init__(parent, style="TFrame", **kwargs)
        self._is_visible = False
        self._show_toggle = show_toggle
        self._var = tk.StringVar()

        # Entry field
        self._entry = tk.Entry(
            self,
            textvariable=self._var,
            show="●",
            font=font or FONTS["mono"],
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"],
        )
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(10, 0))

        if show_toggle:
            self._toggle_btn = tk.Button(
                self,
                text="👁",
                font=FONTS["body"],
                bg=COLORS["input_bg"],
                fg=COLORS["text_secondary"],
                activebackground=COLORS["surface_light"],
                activeforeground=COLORS["primary"],
                relief=tk.FLAT,
                borderwidth=0,
                cursor="hand2",
                width=3,
                command=self._toggle_visibility,
            )
            self._toggle_btn.pack(side=tk.RIGHT, padx=(0, 5), ipady=8)

    def _toggle_visibility(self):
        """Toggle password visibility."""
        self._is_visible = not self._is_visible
        if self._is_visible:
            self._entry.configure(show="")
            self._toggle_btn.configure(text="🔒")
        else:
            self._entry.configure(show="●")
            self._toggle_btn.configure(text="👁")

    def get(self) -> str:
        """Get the current password text."""
        return self._var.get()

    def set(self, text: str):
        """Set the password text."""
        self._var.set(text)

    def clear(self):
        """Clear the password field."""
        self._var.set("")

    def bind_change(self, callback):
        """Bind a callback to text changes (for strength meter)."""
        self._var.trace_add("write", lambda *args: callback(self._var.get()))

    @property
    def variable(self) -> tk.StringVar:
        """Access the underlying StringVar."""
        return self._var

    def set_readonly(self, readonly: bool = True):
        """Set the field to read-only (or editable)."""
        state = "readonly" if readonly else "normal"
        self._entry.configure(state=state)

    def focus_set(self):
        """Set focus to the entry."""
        self._entry.focus_set()
