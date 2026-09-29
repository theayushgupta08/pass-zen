"""
PassZen Add Entry Screen — Generate or store a password.

Two modes:
- Generate: User enters website + username, app generates the password.
- Store:    User enters website + username + their own password.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, List

from src.ui.theme import COLORS, FONTS
from src.ui.components.password_field import PasswordField
from src.ui.components.strength_meter import StrengthMeter
from src.ui.components.tag_selector import TagSelector
from src.models.entry import PasswordEntry
from src.crypto.password_gen import generate_password


class AddEntryScreen(ttk.Frame):
    """
    Add a new password entry — generate or store mode.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_save: Callable[[PasswordEntry], None],
        on_cancel: Callable,
        categories: List[str],
        settings_manager=None,
        **kwargs,
    ):
        super().__init__(parent, style="TFrame", **kwargs)
        self._on_save = on_save
        self._on_cancel = on_cancel
        self._categories = categories
        self._settings = settings_manager
        self._mode = "generate"  # "generate" or "store"

        self._build_ui()

    def _build_ui(self):
        """Build the add entry form."""
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
            command=self._on_cancel,
        )
        back_btn.pack(side=tk.LEFT)

        title = tk.Label(
            header,
            text="Add Password",
            font=FONTS["heading"],
            bg=COLORS["bg"],
            fg=COLORS["text"],
        )
        title.pack(side=tk.LEFT, padx=(16, 0))

        # ── Mode toggle ─────────────────────────────────────────────
        mode_frame = tk.Frame(self, bg=COLORS["bg"])
        mode_frame.pack(fill=tk.X, padx=20, pady=(20, 0))

        self._gen_btn = tk.Button(
            mode_frame,
            text="🎲 Generate Password",
            font=FONTS["body_sm_bold"],
            bg=COLORS["primary"],
            fg="#FFFFFF",
            activebackground=COLORS["primary_hover"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            pady=6,
            command=lambda: self._set_mode("generate"),
        )
        self._gen_btn.pack(side=tk.LEFT, padx=(0, 8))

        self._store_btn = tk.Button(
            mode_frame,
            text="📝 Store Existing",
            font=FONTS["body_sm"],
            bg=COLORS["surface"],
            fg=COLORS["text_secondary"],
            activebackground=COLORS["surface_hover"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            pady=6,
            command=lambda: self._set_mode("store"),
        )
        self._store_btn.pack(side=tk.LEFT)

        # ── Form ─────────────────────────────────────────────────────
        self._form_frame = tk.Frame(self, bg=COLORS["bg"])
        self._form_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=(24, 20))

        self._build_form()

    def _set_mode(self, mode: str):
        """Switch between generate and store modes."""
        self._mode = mode

        if mode == "generate":
            self._gen_btn.configure(
                bg=COLORS["primary"], fg="#FFFFFF",
                font=FONTS["body_sm_bold"],
            )
            self._store_btn.configure(
                bg=COLORS["surface"], fg=COLORS["text_secondary"],
                font=FONTS["body_sm"],
            )
        else:
            self._store_btn.configure(
                bg=COLORS["primary"], fg="#FFFFFF",
                font=FONTS["body_sm_bold"],
            )
            self._gen_btn.configure(
                bg=COLORS["surface"], fg=COLORS["text_secondary"],
                font=FONTS["body_sm"],
            )

        self._build_form()

    def _build_form(self):
        """Build the form fields based on current mode."""
        for widget in self._form_frame.winfo_children():
            widget.destroy()

        # ── Website/Nickname ─────────────────────────────────────────
        tk.Label(
            self._form_frame,
            text="Website / Nickname",
            font=FONTS["body_sm_bold"],
            bg=COLORS["bg"],
            fg=COLORS["text"],
        ).pack(anchor=tk.W, pady=(0, 4))

        self._website_var = tk.StringVar()
        website_entry = tk.Entry(
            self._form_frame,
            textvariable=self._website_var,
            font=FONTS["body"],
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"],
        )
        website_entry.pack(fill=tk.X, ipady=10, pady=(0, 16))
        website_entry.focus_set()

        # ── Username/Email ───────────────────────────────────────────
        tk.Label(
            self._form_frame,
            text="Username / Email",
            font=FONTS["body_sm_bold"],
            bg=COLORS["bg"],
            fg=COLORS["text"],
        ).pack(anchor=tk.W, pady=(0, 4))

        self._username_var = tk.StringVar()
        username_entry = tk.Entry(
            self._form_frame,
            textvariable=self._username_var,
            font=FONTS["body"],
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"],
        )
        username_entry.pack(fill=tk.X, ipady=10, pady=(0, 16))

        # ── Password ────────────────────────────────────────────────
        tk.Label(
            self._form_frame,
            text="Password",
            font=FONTS["body_sm_bold"],
            bg=COLORS["bg"],
            fg=COLORS["text"],
        ).pack(anchor=tk.W, pady=(0, 4))

        if self._mode == "generate":
            # Generated password (read-only with regenerate button)
            gen_frame = tk.Frame(self._form_frame, bg=COLORS["bg"])
            gen_frame.pack(fill=tk.X, pady=(0, 4))

            self._password_field = PasswordField(
                gen_frame, show_toggle=True
            )
            self._password_field.pack(side=tk.LEFT, fill=tk.X, expand=True)

            regen_btn = tk.Button(
                gen_frame,
                text="🔄",
                font=FONTS["body"],
                bg=COLORS["surface"],
                fg=COLORS["text_secondary"],
                activebackground=COLORS["surface_hover"],
                activeforeground=COLORS["secondary"],
                relief=tk.FLAT,
                cursor="hand2",
                width=3,
                command=self._regenerate_password,
            )
            regen_btn.pack(side=tk.RIGHT, padx=(8, 0), ipady=8)

            # Generate initial password
            self._regenerate_password()

            # Strength meter for generated password
            self._strength_meter = StrengthMeter(self._form_frame)
            self._strength_meter.pack(fill=tk.X, pady=(0, 16))
            self._strength_meter.update(self._password_field.get())

        else:
            # Manual password entry
            self._password_field = PasswordField(
                self._form_frame, show_toggle=True
            )
            self._password_field.pack(fill=tk.X, pady=(0, 4))

            # Strength meter
            self._strength_meter = StrengthMeter(self._form_frame)
            self._strength_meter.pack(fill=tk.X, pady=(0, 16))

            # Bind real-time strength updates
            self._password_field.bind_change(self._strength_meter.update)

        # ── Category ─────────────────────────────────────────────────
        tk.Label(
            self._form_frame,
            text="Category",
            font=FONTS["body_sm_bold"],
            bg=COLORS["bg"],
            fg=COLORS["text"],
        ).pack(anchor=tk.W, pady=(0, 4))

        self._tag_selector = TagSelector(
            self._form_frame,
            categories=self._categories,
            default="Other",
        )
        self._tag_selector.pack(fill=tk.X, pady=(0, 24))

        # ── Save button ──────────────────────────────────────────────
        save_btn = tk.Button(
            self._form_frame,
            text="💾 Save Password",
            font=FONTS["body_bold"],
            bg=COLORS["primary"],
            fg="#FFFFFF",
            activebackground=COLORS["primary_hover"],
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            pady=12,
            command=self._save,
        )
        save_btn.pack(fill=tk.X)

    def _regenerate_password(self):
        """Generate a new password using current settings."""
        length = 12
        use_upper = True
        use_lower = True
        use_digits = True
        use_symbols = True

        if self._settings:
            length = self._settings.get("password_length", 12)
            use_upper = self._settings.get("use_uppercase", True)
            use_lower = self._settings.get("use_lowercase", True)
            use_digits = self._settings.get("use_digits", True)
            use_symbols = self._settings.get("use_symbols", True)

        password = generate_password(
            length=length,
            use_uppercase=use_upper,
            use_lowercase=use_lower,
            use_digits=use_digits,
            use_symbols=use_symbols,
        )
        self._password_field.set(password)

        if hasattr(self, "_strength_meter"):
            self._strength_meter.update(password)

    def _save(self):
        """Validate and save the entry."""
        website = self._website_var.get().strip()
        username = self._username_var.get().strip()
        password = self._password_field.get().strip()

        if not website:
            self._show_error("Please enter a website or nickname.")
            return
        if not username:
            self._show_error("Please enter a username or email.")
            return
        if not password:
            self._show_error("Please enter or generate a password.")
            return

        entry = PasswordEntry(
            website=website,
            username=username,
            password=password,
            category=self._tag_selector.get(),
        )

        self._on_save(entry)

    def _show_error(self, message: str):
        """Show an error message."""
        from tkinter import messagebox
        messagebox.showwarning(
            "Missing Information", message,
            parent=self.winfo_toplevel(),
        )
