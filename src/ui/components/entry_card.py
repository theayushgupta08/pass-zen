"""
PassZen Entry Card — Password entry display widget for the dashboard.

Each card shows the website name, username, masked password, and action buttons
(show/hide, copy, edit, delete).
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable

from src.ui.theme import COLORS, FONTS
from src.models.entry import PasswordEntry


class EntryCard(tk.Frame):
    """
    A card widget displaying a single password entry.

    Shows website, username, masked password, category tag, and action buttons.
    """

    # Category emoji mapping
    CATEGORY_EMOJIS = {
        "Social Media": "🌐",
        "Email": "📧",
        "Banking": "🏦",
        "Shopping": "🛒",
        "Work": "💼",
        "Entertainment": "🎮",
        "Other": "📁",
    }

    def __init__(
        self,
        parent: tk.Widget,
        entry: PasswordEntry,
        on_copy: Callable[[PasswordEntry], None],
        on_edit: Callable[[PasswordEntry], None],
        on_delete: Callable[[PasswordEntry], None],
        allow_view: bool = False,
        **kwargs,
    ):
        super().__init__(
            parent,
            bg=COLORS["surface"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border"],
            **kwargs,
        )
        self._entry = entry
        self._on_copy = on_copy
        self._on_edit = on_edit
        self._on_delete = on_delete
        self._allow_view = allow_view
        self._password_visible = False

        self.configure(padx=16, pady=12)
        self._build_ui()

        # Hover effect
        self.bind("<Enter>", self._on_hover_enter)
        self.bind("<Leave>", self._on_hover_leave)

    def _build_ui(self):
        """Build the card UI."""
        bg = COLORS["surface"]

        # ── Top row: Website + Category ──────────────────────────────
        top_frame = tk.Frame(self, bg=bg)
        top_frame.pack(fill=tk.X, pady=(0, 4))

        emoji = self.CATEGORY_EMOJIS.get(self._entry.category, "📁")
        website_label = tk.Label(
            top_frame,
            text=f"{emoji}  {self._entry.website}",
            font=FONTS["heading_sm"],
            bg=bg,
            fg=COLORS["text"],
            anchor=tk.W,
        )
        website_label.pack(side=tk.LEFT)

        category_label = tk.Label(
            top_frame,
            text=self._entry.category,
            font=FONTS["caption"],
            bg=COLORS["surface_light"],
            fg=COLORS["text_secondary"],
            padx=8,
            pady=2,
        )
        category_label.pack(side=tk.RIGHT)

        # ── Username row ─────────────────────────────────────────────
        username_label = tk.Label(
            self,
            text=f"👤  {self._entry.username}",
            font=FONTS["body_sm"],
            bg=bg,
            fg=COLORS["text_secondary"],
            anchor=tk.W,
        )
        username_label.pack(fill=tk.X, pady=(0, 8))

        # ── Password row + actions ───────────────────────────────────
        bottom_frame = tk.Frame(self, bg=bg)
        bottom_frame.pack(fill=tk.X)

        # Password display
        self._password_label = tk.Label(
            bottom_frame,
            text="🔑  ●●●●●●●●●●●●",
            font=FONTS["mono"],
            bg=bg,
            fg=COLORS["text_dim"],
            anchor=tk.W,
        )
        self._password_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Action buttons
        actions_frame = tk.Frame(bottom_frame, bg=bg)
        actions_frame.pack(side=tk.RIGHT)

        # View/Hide button (only if allowed)
        if self._allow_view:
            self._view_btn = tk.Button(
                actions_frame,
                text="👁",
                font=FONTS["body"],
                bg=bg,
                fg=COLORS["text_secondary"],
                activebackground=COLORS["surface_hover"],
                activeforeground=COLORS["primary"],
                relief=tk.FLAT,
                borderwidth=0,
                cursor="hand2",
                width=3,
                command=self._toggle_password,
            )
            self._view_btn.pack(side=tk.LEFT, padx=2)

        # Copy button
        copy_btn = tk.Button(
            actions_frame,
            text="📋",
            font=FONTS["body"],
            bg=bg,
            fg=COLORS["text_secondary"],
            activebackground=COLORS["surface_hover"],
            activeforeground=COLORS["secondary"],
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            width=3,
            command=lambda: self._on_copy(self._entry),
        )
        copy_btn.pack(side=tk.LEFT, padx=2)

        # Edit button
        edit_btn = tk.Button(
            actions_frame,
            text="✏️",
            font=FONTS["body"],
            bg=bg,
            fg=COLORS["text_secondary"],
            activebackground=COLORS["surface_hover"],
            activeforeground=COLORS["warning"],
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            width=3,
            command=lambda: self._on_edit(self._entry),
        )
        edit_btn.pack(side=tk.LEFT, padx=2)

        # Delete button
        delete_btn = tk.Button(
            actions_frame,
            text="🗑️",
            font=FONTS["body"],
            bg=bg,
            fg=COLORS["text_secondary"],
            activebackground=COLORS["surface_hover"],
            activeforeground=COLORS["danger"],
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            width=3,
            command=lambda: self._on_delete(self._entry),
        )
        delete_btn.pack(side=tk.LEFT, padx=2)

    def _toggle_password(self):
        """Toggle password visibility."""
        self._password_visible = not self._password_visible
        if self._password_visible:
            self._password_label.configure(
                text=f"🔑  {self._entry.password}",
                fg=COLORS["secondary"],
            )
            self._view_btn.configure(text="🔒")
        else:
            self._password_label.configure(
                text="🔑  ●●●●●●●●●●●●",
                fg=COLORS["text_dim"],
            )
            self._view_btn.configure(text="👁")

    def _on_hover_enter(self, event=None):
        """Hover enter effect."""
        self.configure(highlightbackground=COLORS["primary"])

    def _on_hover_leave(self, event=None):
        """Hover leave effect."""
        self.configure(highlightbackground=COLORS["border"])
