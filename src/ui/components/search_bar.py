"""
PassZen Search Bar — Real-time search/filter component.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable

from src.ui.theme import COLORS, FONTS


class SearchBar(ttk.Frame):
    """
    A search bar with a search icon and real-time filtering.

    Fires the `on_search` callback on every keystroke with the current query.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_search: Callable[[str], None],
        placeholder: str = "Search passwords...",
        **kwargs,
    ):
        super().__init__(parent, style="TFrame", **kwargs)
        self._on_search = on_search
        self._placeholder = placeholder

        # Container with border
        self._container = tk.Frame(
            self,
            bg=COLORS["input_bg"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"],
        )
        self._container.pack(fill=tk.X)

        # Search icon
        self._icon = tk.Label(
            self._container,
            text="🔍",
            font=FONTS["body"],
            bg=COLORS["input_bg"],
            fg=COLORS["text_secondary"],
        )
        self._icon.pack(side=tk.LEFT, padx=(10, 0))

        # Entry
        self._var = tk.StringVar()
        self._entry = tk.Entry(
            self._container,
            textvariable=self._var,
            font=FONTS["body"],
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            borderwidth=0,
        )
        self._entry.pack(
            side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(8, 10)
        )

        # Clear button (shown when there's text)
        self._clear_btn = tk.Button(
            self._container,
            text="✕",
            font=FONTS["body_sm"],
            bg=COLORS["input_bg"],
            fg=COLORS["text_dim"],
            activebackground=COLORS["input_bg"],
            activeforeground=COLORS["text"],
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            command=self.clear,
        )

        # Placeholder
        self._show_placeholder()

        # Bindings
        self._entry.bind("<FocusIn>", self._on_focus_in)
        self._entry.bind("<FocusOut>", self._on_focus_out)
        self._var.trace_add("write", self._on_change)

    def _show_placeholder(self):
        """Show the placeholder text."""
        if not self._var.get():
            self._entry.configure(fg=COLORS["text_dim"])
            self._var.set(self._placeholder)
            self._is_placeholder = True

    def _on_focus_in(self, event=None):
        """Handle focus in — remove placeholder."""
        if hasattr(self, "_is_placeholder") and self._is_placeholder:
            self._var.set("")
            self._entry.configure(fg=COLORS["text"])
            self._is_placeholder = False

    def _on_focus_out(self, event=None):
        """Handle focus out — show placeholder if empty."""
        if not self._var.get():
            self._show_placeholder()

    def _on_change(self, *args):
        """Handle text change — fire search callback and toggle clear button."""
        if hasattr(self, "_is_placeholder") and self._is_placeholder:
            return

        query = self._var.get()

        if query:
            self._clear_btn.pack(side=tk.RIGHT, padx=(0, 8))
        else:
            self._clear_btn.pack_forget()

        self._on_search(query)

    def clear(self):
        """Clear the search bar."""
        self._var.set("")
        self._clear_btn.pack_forget()
        self._entry.focus_set()
        self._on_search("")

    def get(self) -> str:
        """Get the current search query."""
        if hasattr(self, "_is_placeholder") and self._is_placeholder:
            return ""
        return self._var.get()
