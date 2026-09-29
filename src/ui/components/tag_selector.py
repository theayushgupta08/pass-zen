"""
PassZen Tag Selector — Category/tag picker dropdown with custom tag creation.
"""

import tkinter as tk
from tkinter import ttk, simpledialog
from typing import List, Callable, Optional

from src.ui.theme import COLORS, FONTS


class TagSelector(ttk.Frame):
    """
    A category selector combining a dropdown of existing categories
    with the ability to create new custom tags.
    """

    def __init__(
        self,
        parent: tk.Widget,
        categories: List[str],
        on_change: Optional[Callable[[str], None]] = None,
        default: str = "Other",
        allow_create: bool = True,
        **kwargs,
    ):
        super().__init__(parent, style="TFrame", **kwargs)
        self._categories = list(categories)
        self._on_change = on_change
        self._allow_create = allow_create

        # Variable
        self._var = tk.StringVar(value=default)

        # Container
        container = ttk.Frame(self, style="TFrame")
        container.pack(fill=tk.X)

        # Combobox
        values = list(self._categories)
        if allow_create:
            values.append("+ New Category...")

        self._combo = ttk.Combobox(
            container,
            textvariable=self._var,
            values=values,
            state="readonly",
            style="TCombobox",
            font=FONTS["body"],
        )
        self._combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Bind selection
        self._combo.bind("<<ComboboxSelected>>", self._on_select)

    def _on_select(self, event=None):
        """Handle dropdown selection."""
        selected = self._var.get()

        if selected == "+ New Category...":
            # Prompt for new category name
            new_name = simpledialog.askstring(
                "New Category",
                "Enter category name:",
                parent=self.winfo_toplevel(),
            )
            if new_name and new_name.strip():
                name = new_name.strip()
                if name not in self._categories:
                    self._categories.append(name)
                    self._refresh_values()
                self._var.set(name)
            else:
                self._var.set("Other")

        if self._on_change:
            self._on_change(self._var.get())

    def _refresh_values(self):
        """Refresh the combobox values."""
        values = list(self._categories)
        if self._allow_create:
            values.append("+ New Category...")
        self._combo.configure(values=values)

    def get(self) -> str:
        """Get the selected category."""
        value = self._var.get()
        if value == "+ New Category...":
            return "Other"
        return value

    def set(self, value: str):
        """Set the selected category."""
        self._var.set(value)

    def update_categories(self, categories: List[str]):
        """Update the list of available categories."""
        self._categories = list(categories)
        self._refresh_values()
