"""
PassZen Edit Entry Screen — Edit or delete an existing password entry.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, List

from src.ui.theme import COLORS, FONTS
from src.ui.components.password_field import PasswordField
from src.ui.components.strength_meter import StrengthMeter
from src.ui.components.tag_selector import TagSelector
from src.models.entry import PasswordEntry
from src.crypto.password_gen import generate_password


class EditEntryScreen(ttk.Frame):
    """
    Edit an existing password entry.
    Pre-populated with the entry's current values.
    """

    def __init__(
        self,
        parent: tk.Widget,
        entry: PasswordEntry,
        on_save: Callable[[PasswordEntry], None],
        on_delete: Callable[[str], None],
        on_cancel: Callable,
        categories: List[str],
        settings_manager=None,
        **kwargs,
    ):
        super().__init__(parent, style="TFrame", **kwargs)
        self._entry = entry
        self._on_save = on_save
        self._on_delete = on_delete
        self._on_cancel = on_cancel
        self._categories = categories
        self._settings = settings_manager

        self._build_ui()

    def _build_ui(self):
        """Build the edit form."""
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
            text=f"Edit — {self._entry.website}",
            font=FONTS["heading"],
            bg=COLORS["bg"],
            fg=COLORS["text"],
        )
        title.pack(side=tk.LEFT, padx=(16, 0))

        # ── Form ─────────────────────────────────────────────────────
        form = tk.Frame(self, bg=COLORS["bg"])
        form.pack(fill=tk.BOTH, expand=True, padx=40, pady=(24, 20))

        # Website/Nickname
        tk.Label(
            form, text="Website / Nickname",
            font=FONTS["body_sm_bold"], bg=COLORS["bg"], fg=COLORS["text"],
        ).pack(anchor=tk.W, pady=(0, 4))

        self._website_var = tk.StringVar(value=self._entry.website)
        tk.Entry(
            form, textvariable=self._website_var, font=FONTS["body"],
            bg=COLORS["input_bg"], fg=COLORS["text"],
            insertbackground=COLORS["text"], relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"],
        ).pack(fill=tk.X, ipady=10, pady=(0, 16))

        # Username/Email
        tk.Label(
            form, text="Username / Email",
            font=FONTS["body_sm_bold"], bg=COLORS["bg"], fg=COLORS["text"],
        ).pack(anchor=tk.W, pady=(0, 4))

        self._username_var = tk.StringVar(value=self._entry.username)
        tk.Entry(
            form, textvariable=self._username_var, font=FONTS["body"],
            bg=COLORS["input_bg"], fg=COLORS["text"],
            insertbackground=COLORS["text"], relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"],
        ).pack(fill=tk.X, ipady=10, pady=(0, 16))

        # Password with regenerate
        tk.Label(
            form, text="Password",
            font=FONTS["body_sm_bold"], bg=COLORS["bg"], fg=COLORS["text"],
        ).pack(anchor=tk.W, pady=(0, 4))

        pass_frame = tk.Frame(form, bg=COLORS["bg"])
        pass_frame.pack(fill=tk.X, pady=(0, 4))

        self._password_field = PasswordField(pass_frame, show_toggle=True)
        self._password_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._password_field.set(self._entry.password)

        regen_btn = tk.Button(
            pass_frame,
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

        # Strength meter
        self._strength_meter = StrengthMeter(form)
        self._strength_meter.pack(fill=tk.X, pady=(0, 16))
        self._strength_meter.update(self._entry.password)

        # Bind real-time updates
        self._password_field.bind_change(self._strength_meter.update)

        # Category
        tk.Label(
            form, text="Category",
            font=FONTS["body_sm_bold"], bg=COLORS["bg"], fg=COLORS["text"],
        ).pack(anchor=tk.W, pady=(0, 4))

        self._tag_selector = TagSelector(
            form,
            categories=self._categories,
            default=self._entry.category,
        )
        self._tag_selector.pack(fill=tk.X, pady=(0, 24))

        # ── Action buttons ───────────────────────────────────────────
        btn_frame = tk.Frame(form, bg=COLORS["bg"])
        btn_frame.pack(fill=tk.X)

        save_btn = tk.Button(
            btn_frame,
            text="💾 Save Changes",
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
        save_btn.pack(fill=tk.X, pady=(0, 8))

        delete_btn = tk.Button(
            btn_frame,
            text="🗑️ Delete Entry",
            font=FONTS["body"],
            bg=COLORS["surface"],
            fg=COLORS["danger"],
            activebackground=COLORS["surface_hover"],
            activeforeground=COLORS["danger"],
            relief=tk.FLAT,
            cursor="hand2",
            pady=10,
            command=self._delete,
        )
        delete_btn.pack(fill=tk.X)

        # ── Metadata ─────────────────────────────────────────────────
        meta_frame = tk.Frame(form, bg=COLORS["bg"])
        meta_frame.pack(fill=tk.X, pady=(16, 0))

        created = self._entry.created_at[:10] if self._entry.created_at else "—"
        updated = self._entry.updated_at[:10] if self._entry.updated_at else "—"

        tk.Label(
            meta_frame,
            text=f"Created: {created}  •  Last modified: {updated}",
            font=FONTS["caption"],
            bg=COLORS["bg"],
            fg=COLORS["text_dim"],
        ).pack(anchor=tk.W)

    def _regenerate_password(self):
        """Generate a new password."""
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
        self._strength_meter.update(password)

    def _save(self):
        """Validate and save changes."""
        website = self._website_var.get().strip()
        username = self._username_var.get().strip()
        password = self._password_field.get().strip()

        if not website:
            messagebox.showwarning(
                "Missing", "Please enter a website or nickname.",
                parent=self.winfo_toplevel(),
            )
            return
        if not username:
            messagebox.showwarning(
                "Missing", "Please enter a username or email.",
                parent=self.winfo_toplevel(),
            )
            return
        if not password:
            messagebox.showwarning(
                "Missing", "Please enter a password.",
                parent=self.winfo_toplevel(),
            )
            return

        self._entry.website = website
        self._entry.username = username
        self._entry.password = password
        self._entry.category = self._tag_selector.get()

        self._on_save(self._entry)

    def _delete(self):
        """Confirm and delete the entry."""
        result = messagebox.askyesno(
            "Delete Entry",
            f"Are you sure you want to delete \"{self._entry.website}\"?\n\n"
            f"This cannot be undone.",
            parent=self.winfo_toplevel(),
        )
        if result:
            self._on_delete(self._entry.id)
