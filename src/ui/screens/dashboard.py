"""
PassZen Dashboard — Main vault view with scrollable entry list, search,
category filtering, and entry actions.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, List

from src.ui.theme import COLORS, FONTS
from src.ui.components.search_bar import SearchBar
from src.ui.components.entry_card import EntryCard
from src.models.entry import PasswordEntry
from src.storage.database import Database
from src.utils.clipboard import ClipboardManager


class Dashboard(ttk.Frame):
    """
    Main dashboard view — lists all password entries with search and filter.
    """

    def __init__(
        self,
        parent: tk.Widget,
        db: Database,
        clipboard: ClipboardManager,
        on_add: Callable,
        on_edit: Callable[[PasswordEntry], None],
        on_settings: Callable,
        on_lock: Callable,
        on_export_import: Callable,
        settings_manager=None,
        **kwargs,
    ):
        super().__init__(parent, style="TFrame", **kwargs)
        self._db = db
        self._clipboard = clipboard
        self._on_add = on_add
        self._on_edit = on_edit
        self._on_settings = on_settings
        self._on_lock = on_lock
        self._on_export_import = on_export_import
        self._settings = settings_manager
        self._current_category = "All"
        self._search_query = ""

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        """Build the dashboard layout."""
        # ── Header ───────────────────────────────────────────────────
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill=tk.X, padx=20, pady=(16, 0))

        title = tk.Label(
            header,
            text="🔐 PassZen",
            font=FONTS["heading_lg"],
            bg=COLORS["bg"],
            fg=COLORS["text"],
        )
        title.pack(side=tk.LEFT)

        # Header buttons (right side)
        btn_frame = tk.Frame(header, bg=COLORS["bg"])
        btn_frame.pack(side=tk.RIGHT)

        # Export/Import
        export_btn = tk.Button(
            btn_frame,
            text="📦",
            font=FONTS["body"],
            bg=COLORS["bg"],
            fg=COLORS["text_secondary"],
            activebackground=COLORS["surface"],
            activeforeground=COLORS["text"],
            relief=tk.FLAT,
            cursor="hand2",
            width=3,
            command=self._on_export_import,
        )
        export_btn.pack(side=tk.LEFT, padx=2)

        settings_btn = tk.Button(
            btn_frame,
            text="⚙️",
            font=FONTS["body"],
            bg=COLORS["bg"],
            fg=COLORS["text_secondary"],
            activebackground=COLORS["surface"],
            activeforeground=COLORS["text"],
            relief=tk.FLAT,
            cursor="hand2",
            width=3,
            command=self._on_settings,
        )
        settings_btn.pack(side=tk.LEFT, padx=2)

        lock_btn = tk.Button(
            btn_frame,
            text="🔒",
            font=FONTS["body"],
            bg=COLORS["bg"],
            fg=COLORS["text_secondary"],
            activebackground=COLORS["surface"],
            activeforeground=COLORS["danger"],
            relief=tk.FLAT,
            cursor="hand2",
            width=3,
            command=self._on_lock,
        )
        lock_btn.pack(side=tk.LEFT, padx=2)

        # ── Search + Add button row ──────────────────────────────────
        search_row = tk.Frame(self, bg=COLORS["bg"])
        search_row.pack(fill=tk.X, padx=20, pady=(16, 0))

        search = SearchBar(search_row, on_search=self._on_search)
        search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))

        add_btn = tk.Button(
            search_row,
            text="+ Add",
            font=FONTS["body_bold"],
            bg=COLORS["primary"],
            fg="#FFFFFF",
            activebackground=COLORS["primary_hover"],
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8,
            command=self._on_add,
        )
        add_btn.pack(side=tk.RIGHT)

        # ── Category filter tabs ─────────────────────────────────────
        self._filter_frame = tk.Frame(self, bg=COLORS["bg"])
        self._filter_frame.pack(fill=tk.X, padx=20, pady=(12, 0))

        self._build_category_filters()

        # ── Separator ────────────────────────────────────────────────
        sep = tk.Frame(self, bg=COLORS["border"], height=1)
        sep.pack(fill=tk.X, padx=20, pady=(12, 0))

        # ── Scrollable entry list ────────────────────────────────────
        list_container = tk.Frame(self, bg=COLORS["bg"])
        list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(8, 0))

        # Canvas + scrollbar for scrolling
        self._canvas = tk.Canvas(
            list_container, bg=COLORS["bg"], highlightthickness=0
        )
        self._scrollbar = ttk.Scrollbar(
            list_container,
            orient=tk.VERTICAL,
            command=self._canvas.yview,
            style="Vertical.TScrollbar",
        )
        self._scrollable_frame = tk.Frame(self._canvas, bg=COLORS["bg"])

        self._scrollable_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")
            ),
        )

        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._scrollable_frame, anchor=tk.NW
        )

        # Make the scrollable frame expand to canvas width
        self._canvas.bind(
            "<Configure>",
            lambda e: self._canvas.itemconfig(
                self._canvas_window, width=e.width
            ),
        )

        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Mouse wheel scrolling
        self._canvas.bind_all(
            "<MouseWheel>",
            lambda e: self._canvas.yview_scroll(
                int(-1 * (e.delta / 120)), "units"
            ),
        )

        # ── Status bar ───────────────────────────────────────────────
        self._status_frame = tk.Frame(self, bg=COLORS["surface"], height=36)
        self._status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self._status_frame.pack_propagate(False)

        self._entry_count_label = tk.Label(
            self._status_frame,
            text="",
            font=FONTS["caption"],
            bg=COLORS["surface"],
            fg=COLORS["text_secondary"],
        )
        self._entry_count_label.pack(side=tk.LEFT, padx=20)

        self._timer_label = tk.Label(
            self._status_frame,
            text="",
            font=FONTS["caption"],
            bg=COLORS["surface"],
            fg=COLORS["text_dim"],
        )
        self._timer_label.pack(side=tk.RIGHT, padx=20)

    def _build_category_filters(self):
        """Build the category filter buttons."""
        for widget in self._filter_frame.winfo_children():
            widget.destroy()

        categories = ["All"] + [c.name for c in self._db.get_all_categories()]

        for cat in categories:
            is_active = cat == self._current_category
            style = "FilterActive.TButton" if is_active else "Filter.TButton"

            btn = ttk.Button(
                self._filter_frame,
                text=cat,
                style=style,
                command=lambda c=cat: self._on_category_filter(c),
            )
            btn.pack(side=tk.LEFT, padx=(0, 6))

    def _on_category_filter(self, category: str):
        """Handle category filter selection."""
        self._current_category = category
        self._build_category_filters()
        self.refresh()

    def _on_search(self, query: str):
        """Handle search query change."""
        self._search_query = query
        self.refresh()

    def refresh(self):
        """Refresh the entry list based on current search/filter."""
        # Clear existing cards
        for widget in self._scrollable_frame.winfo_children():
            widget.destroy()

        # Fetch and filter entries
        entries = self._db.search_entries(
            self._search_query, self._current_category
        )

        allow_view = True
        if self._settings:
            allow_view = self._settings.get("password_visibility") == "viewable"

        if not entries:
            # Empty state
            empty_frame = tk.Frame(self._scrollable_frame, bg=COLORS["bg"])
            empty_frame.pack(fill=tk.BOTH, expand=True, pady=60)

            if self._search_query or self._current_category != "All":
                empty_text = "No matching passwords found"
                empty_sub = "Try a different search or filter"
            else:
                empty_text = "No passwords yet"
                empty_sub = 'Click "+ Add" to store your first password'

            tk.Label(
                empty_frame,
                text="🔐",
                font=(FONTS["heading_xl"][0], 48),
                bg=COLORS["bg"],
                fg=COLORS["text_dim"],
            ).pack()

            tk.Label(
                empty_frame,
                text=empty_text,
                font=FONTS["heading_sm"],
                bg=COLORS["bg"],
                fg=COLORS["text_secondary"],
            ).pack(pady=(16, 4))

            tk.Label(
                empty_frame,
                text=empty_sub,
                font=FONTS["body_sm"],
                bg=COLORS["bg"],
                fg=COLORS["text_dim"],
            ).pack()

        else:
            for entry in entries:
                card = EntryCard(
                    self._scrollable_frame,
                    entry=entry,
                    on_copy=self._copy_password,
                    on_edit=self._on_edit,
                    on_delete=self._confirm_delete,
                    allow_view=allow_view,
                )
                card.pack(fill=tk.X, pady=(0, 8))

        # Update status
        total = self._db.get_entry_count()
        shown = len(entries)
        if shown == total:
            self._entry_count_label.configure(
                text=f"  {total} password{'s' if total != 1 else ''}"
            )
        else:
            self._entry_count_label.configure(
                text=f"  Showing {shown} of {total}"
            )

    def _copy_password(self, entry: PasswordEntry):
        """Copy a password to clipboard."""
        self._clipboard.copy(entry.password)

        # Show brief feedback
        clear_time = self._clipboard.clear_seconds
        self._timer_label.configure(
            text=f"📋 Copied! Clearing in {clear_time}s"
        )
        self.after(3000, lambda: self._timer_label.configure(text=""))

    def _confirm_delete(self, entry: PasswordEntry):
        """Show delete confirmation dialog."""
        result = messagebox.askyesno(
            "Delete Entry",
            f"Are you sure you want to delete the entry for "
            f"\"{entry.website}\"?\n\nThis cannot be undone.",
            parent=self.winfo_toplevel(),
        )
        if result:
            self._db.delete_entry(entry.id)
            self.refresh()

    def update_timer_display(self, remaining: int):
        """Update the auto-lock timer display in the status bar."""
        minutes = remaining // 60
        seconds = remaining % 60
        self._timer_label.configure(
            text=f"🔒 Auto-lock: {minutes}:{seconds:02d}"
        )
