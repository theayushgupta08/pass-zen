"""
PassZen Settings Screen — Configurable user preferences.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from src.ui.theme import COLORS, FONTS
from src.utils.settings import SettingsManager
from src.config import MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH


class SettingsScreen(ttk.Frame):
    """
    Settings screen for configuring password generation rules,
    visibility, clipboard, auto-lock, categories, and PIN management.
    """

    def __init__(
        self,
        parent: tk.Widget,
        settings: SettingsManager,
        on_back: Callable,
        on_change_pin: Callable,
        db=None,
        **kwargs,
    ):
        super().__init__(parent, style="TFrame", **kwargs)
        self._settings = settings
        self._on_back = on_back
        self._on_change_pin = on_change_pin
        self._db = db

        self._build_ui()

    def _build_ui(self):
        """Build the settings screen."""
        # ── Header ───────────────────────────────────────────────────
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill=tk.X, padx=20, pady=(16, 0))

        back_btn = tk.Button(
            header,
            text="← Back",
            font=FONTS["body_sm"],
            bg=COLORS["bg"],
            fg=COLORS["text_secondary"],
            activebackground=COLORS["surface"],
            activeforeground=COLORS["text"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self._on_back,
        )
        back_btn.pack(side=tk.LEFT)

        tk.Label(
            header,
            text="⚙️  Settings",
            font=FONTS["heading"],
            bg=COLORS["bg"],
            fg=COLORS["text"],
        ).pack(side=tk.LEFT, padx=(16, 0))

        # ── Scrollable content ───────────────────────────────────────
        canvas = tk.Canvas(self, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=canvas.yview,
        )
        content = tk.Frame(canvas, bg=COLORS["bg"])

        content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas_window = canvas.create_window(
            (0, 0), window=content, anchor=tk.NW
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(canvas_window, width=e.width),
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=16)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )

        # ════════════════════════════════════════════════════════════
        #  PASSWORD GENERATION
        # ════════════════════════════════════════════════════════════
        self._section_header(content, "🎲 Password Generation")

        # Password length
        len_frame = tk.Frame(content, bg=COLORS["bg"])
        len_frame.pack(fill=tk.X, pady=(0, 8))

        tk.Label(
            len_frame, text="Default Length",
            font=FONTS["body"], bg=COLORS["bg"], fg=COLORS["text"],
        ).pack(side=tk.LEFT)

        self._length_var = tk.IntVar(
            value=self._settings.get("password_length", 12)
        )
        self._length_label = tk.Label(
            len_frame,
            text=str(self._length_var.get()),
            font=FONTS["body_bold"],
            bg=COLORS["bg"],
            fg=COLORS["primary"],
            width=4,
        )
        self._length_label.pack(side=tk.RIGHT)

        length_scale = ttk.Scale(
            content,
            from_=MIN_PASSWORD_LENGTH,
            to=MAX_PASSWORD_LENGTH,
            variable=self._length_var,
            orient=tk.HORIZONTAL,
            command=self._on_length_change,
        )
        length_scale.pack(fill=tk.X, pady=(0, 12))

        # Character toggles
        self._upper_var = tk.BooleanVar(
            value=self._settings.get("use_uppercase", True)
        )
        self._make_toggle(content, "Include Uppercase (A-Z)", self._upper_var)

        self._lower_var = tk.BooleanVar(
            value=self._settings.get("use_lowercase", True)
        )
        self._make_toggle(content, "Include Lowercase (a-z)", self._lower_var)

        self._digits_var = tk.BooleanVar(
            value=self._settings.get("use_digits", True)
        )
        self._make_toggle(content, "Include Digits (0-9)", self._digits_var)

        self._symbols_var = tk.BooleanVar(
            value=self._settings.get("use_symbols", True)
        )
        self._make_toggle(
            content, "Include Symbols (!@#$...)", self._symbols_var
        )

        # ════════════════════════════════════════════════════════════
        #  DISPLAY & SECURITY
        # ════════════════════════════════════════════════════════════
        self._section_header(content, "🔐 Display & Security")

        # Password visibility
        vis_frame = tk.Frame(content, bg=COLORS["bg"])
        vis_frame.pack(fill=tk.X, pady=(0, 12))

        tk.Label(
            vis_frame, text="Password Visibility",
            font=FONTS["body"], bg=COLORS["bg"], fg=COLORS["text"],
        ).pack(side=tk.LEFT)

        current_vis = self._settings.get("password_visibility", "copy_only")
        self._vis_var = tk.StringVar(value=current_vis)

        vis_combo = ttk.Combobox(
            vis_frame,
            textvariable=self._vis_var,
            values=["viewable", "copy_only"],
            state="readonly",
            width=12,
        )
        vis_combo.pack(side=tk.RIGHT)

        # Clipboard auto-clear
        clip_frame = tk.Frame(content, bg=COLORS["bg"])
        clip_frame.pack(fill=tk.X, pady=(0, 12))

        tk.Label(
            clip_frame, text="Clipboard Auto-Clear",
            font=FONTS["body"], bg=COLORS["bg"], fg=COLORS["text"],
        ).pack(side=tk.LEFT)

        current_clip = self._settings.get("clipboard_clear_seconds", 30)
        self._clip_var = tk.StringVar(value=str(current_clip))

        clip_combo = ttk.Combobox(
            clip_frame,
            textvariable=self._clip_var,
            values=["15", "30", "60", "0"],
            state="readonly",
            width=8,
        )
        clip_combo.pack(side=tk.RIGHT)

        tk.Label(
            clip_frame, text="seconds (0 = never)",
            font=FONTS["caption"], bg=COLORS["bg"], fg=COLORS["text_dim"],
        ).pack(side=tk.RIGHT, padx=(0, 8))

        # Auto-lock timeout
        lock_frame = tk.Frame(content, bg=COLORS["bg"])
        lock_frame.pack(fill=tk.X, pady=(0, 12))

        tk.Label(
            lock_frame, text="Auto-Lock Timeout",
            font=FONTS["body"], bg=COLORS["bg"], fg=COLORS["text"],
        ).pack(side=tk.LEFT)

        current_lock = self._settings.get("auto_lock_seconds", 180)
        self._lock_var = tk.StringVar(value=str(current_lock))

        lock_combo = ttk.Combobox(
            lock_frame,
            textvariable=self._lock_var,
            values=["60", "180", "300", "600", "0"],
            state="readonly",
            width=8,
        )
        lock_combo.pack(side=tk.RIGHT)

        tk.Label(
            lock_frame, text="seconds (0 = never)",
            font=FONTS["caption"], bg=COLORS["bg"], fg=COLORS["text_dim"],
        ).pack(side=tk.RIGHT, padx=(0, 8))

        # ════════════════════════════════════════════════════════════
        #  CATEGORIES
        # ════════════════════════════════════════════════════════════
        if self._db:
            self._section_header(content, "🏷️ Categories")

            categories = self._db.get_all_categories()

            for cat in categories:
                cat_frame = tk.Frame(content, bg=COLORS["bg"])
                cat_frame.pack(fill=tk.X, pady=2)

                prefix = "📌" if not cat.is_custom else "🏷️"
                tk.Label(
                    cat_frame,
                    text=f"  {prefix}  {cat.name}",
                    font=FONTS["body"],
                    bg=COLORS["bg"],
                    fg=COLORS["text"],
                ).pack(side=tk.LEFT)

                if cat.is_custom:
                    del_btn = tk.Button(
                        cat_frame,
                        text="✕",
                        font=FONTS["body_sm"],
                        bg=COLORS["bg"],
                        fg=COLORS["text_dim"],
                        activeforeground=COLORS["danger"],
                        relief=tk.FLAT,
                        cursor="hand2",
                        command=lambda c=cat: self._delete_category(c.id, c.name),
                    )
                    del_btn.pack(side=tk.RIGHT)

            # Add category button
            add_cat_btn = tk.Button(
                content,
                text="+ Add Category",
                font=FONTS["body_sm"],
                bg=COLORS["surface"],
                fg=COLORS["text_secondary"],
                activebackground=COLORS["surface_hover"],
                relief=tk.FLAT,
                cursor="hand2",
                padx=12,
                pady=6,
                command=self._add_category,
            )
            add_cat_btn.pack(anchor=tk.W, pady=(8, 0))

        # ════════════════════════════════════════════════════════════
        #  ACCOUNT
        # ════════════════════════════════════════════════════════════
        self._section_header(content, "👤 Account")

        change_pin_btn = tk.Button(
            content,
            text="🔑 Change PIN",
            font=FONTS["body"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
            activebackground=COLORS["surface_hover"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            pady=8,
            command=self._on_change_pin,
        )
        change_pin_btn.pack(anchor=tk.W, pady=(0, 8))

        # ── Save button ──────────────────────────────────────────────
        tk.Frame(content, bg=COLORS["border"], height=1).pack(
            fill=tk.X, pady=(20, 16)
        )

        save_btn = tk.Button(
            content,
            text="💾 Save Settings",
            font=FONTS["body_bold"],
            bg=COLORS["primary"],
            fg="#FFFFFF",
            activebackground=COLORS["primary_hover"],
            relief=tk.FLAT,
            cursor="hand2",
            pady=12,
            command=self._save_all,
        )
        save_btn.pack(fill=tk.X)

    def _section_header(self, parent, text: str):
        """Create a section header with divider."""
        tk.Frame(parent, bg=COLORS["border"], height=1).pack(
            fill=tk.X, pady=(16, 12)
        )
        tk.Label(
            parent,
            text=text,
            font=FONTS["heading_sm"],
            bg=COLORS["bg"],
            fg=COLORS["text"],
        ).pack(anchor=tk.W, pady=(0, 8))

    def _make_toggle(self, parent, text: str, variable: tk.BooleanVar):
        """Create a toggle checkbox row."""
        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.pack(fill=tk.X, pady=2)

        ttk.Checkbutton(
            frame,
            text=f"  {text}",
            variable=variable,
            style="TCheckbutton",
        ).pack(side=tk.LEFT)

    def _on_length_change(self, value):
        """Handle slider change."""
        self._length_label.configure(text=str(int(float(value))))

    def _delete_category(self, cat_id: str, cat_name: str):
        """Delete a custom category."""
        result = messagebox.askyesno(
            "Delete Category",
            f"Delete \"{cat_name}\"? Entries will be moved to \"Other\".",
            parent=self.winfo_toplevel(),
        )
        if result and self._db:
            self._db.delete_category(cat_id)
            self._build_ui()

    def _add_category(self):
        """Add a new custom category."""
        from tkinter import simpledialog
        name = simpledialog.askstring(
            "New Category",
            "Enter category name:",
            parent=self.winfo_toplevel(),
        )
        if name and name.strip() and self._db:
            result = self._db.add_category(name.strip())
            if result:
                self._build_ui()
            else:
                messagebox.showinfo(
                    "Exists",
                    "This category already exists.",
                    parent=self.winfo_toplevel(),
                )

    def _save_all(self):
        """Save all settings."""
        self._settings.set("password_length", int(float(self._length_var.get())))
        self._settings.set("use_uppercase", self._upper_var.get())
        self._settings.set("use_lowercase", self._lower_var.get())
        self._settings.set("use_digits", self._digits_var.get())
        self._settings.set("use_symbols", self._symbols_var.get())
        self._settings.set("password_visibility", self._vis_var.get())
        self._settings.set(
            "clipboard_clear_seconds", int(self._clip_var.get())
        )
        self._settings.set("auto_lock_seconds", int(self._lock_var.get()))

        messagebox.showinfo(
            "Saved", "Settings saved successfully!",
            parent=self.winfo_toplevel(),
        )
