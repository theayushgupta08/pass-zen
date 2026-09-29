"""
PassZen Export/Import Screen — Export vault to .passzen file or import from one.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Callable, List

from src.ui.theme import COLORS, FONTS
from src.models.entry import PasswordEntry
from src.storage.export_import import (
    export_vault,
    import_vault,
    find_duplicates,
)
from src.storage.database import Database
from src.crypto.vault import Vault


class ExportImportScreen(ttk.Frame):
    """
    Export/Import screen — export the vault to a file or import from one.
    """

    def __init__(
        self,
        parent: tk.Widget,
        db: Database,
        vault: Vault,
        on_back: Callable,
        **kwargs,
    ):
        super().__init__(parent, style="TFrame", **kwargs)
        self._db = db
        self._vault = vault
        self._on_back = on_back

        self._build_ui()

    def _build_ui(self):
        """Build the export/import screen."""
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
            text="📦 Export / Import",
            font=FONTS["heading"],
            bg=COLORS["bg"],
            fg=COLORS["text"],
        ).pack(side=tk.LEFT, padx=(16, 0))

        # ── Content ──────────────────────────────────────────────────
        content = tk.Frame(self, bg=COLORS["bg"])
        content.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

        # ── Export Section ───────────────────────────────────────────
        export_card = tk.Frame(
            content,
            bg=COLORS["surface"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=24,
            pady=20,
        )
        export_card.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            export_card,
            text="📤 Export Vault",
            font=FONTS["heading_sm"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).pack(anchor=tk.W)

        tk.Label(
            export_card,
            text="Save an encrypted copy of your vault to a .passzen file.\n"
                 "You'll need your current PIN to import it on another machine.",
            font=FONTS["body_sm"],
            bg=COLORS["surface"],
            fg=COLORS["text_secondary"],
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(8, 16))

        entry_count = self._db.get_entry_count()
        tk.Label(
            export_card,
            text=f"Entries to export: {entry_count}",
            font=FONTS["body_sm_bold"],
            bg=COLORS["surface"],
            fg=COLORS["primary"],
        ).pack(anchor=tk.W, pady=(0, 12))

        export_btn = tk.Button(
            export_card,
            text="📁 Choose Location & Export",
            font=FONTS["body_bold"],
            bg=COLORS["primary"],
            fg="#FFFFFF",
            activebackground=COLORS["primary_hover"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=10,
            command=self._export,
        )
        export_btn.pack(anchor=tk.W)

        # ── Import Section ───────────────────────────────────────────
        import_card = tk.Frame(
            content,
            bg=COLORS["surface"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=24,
            pady=20,
        )
        import_card.pack(fill=tk.X)

        tk.Label(
            import_card,
            text="📥 Import Vault",
            font=FONTS["heading_sm"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).pack(anchor=tk.W)

        tk.Label(
            import_card,
            text="Import passwords from a .passzen file.\n"
                 "You'll need the PIN that was used when the file was exported.",
            font=FONTS["body_sm"],
            bg=COLORS["surface"],
            fg=COLORS["text_secondary"],
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(8, 16))

        import_btn = tk.Button(
            import_card,
            text="📂 Choose File & Import",
            font=FONTS["body_bold"],
            bg=COLORS["secondary"],
            fg="#FFFFFF",
            activebackground=COLORS["secondary_hover"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=10,
            command=self._import,
        )
        import_btn.pack(anchor=tk.W)

        # Status label
        self._status = tk.Label(
            content,
            text="",
            font=FONTS["body_sm"],
            bg=COLORS["bg"],
            fg=COLORS["text_secondary"],
        )
        self._status.pack(anchor=tk.W, pady=(20, 0))

    def _export(self):
        """Handle export."""
        filepath = filedialog.asksaveasfilename(
            title="Export Vault",
            defaultextension=".passzen",
            filetypes=[("PassZen Vault", "*.passzen"), ("All Files", "*.*")],
            initialfile="passzen_backup",
            parent=self.winfo_toplevel(),
        )

        if not filepath:
            return

        try:
            entries = self._db.get_all_entries()
            export_vault(entries, self._vault, filepath)

            self._status.configure(
                text=f"✅ Exported {len(entries)} entries to {filepath}",
                fg=COLORS["success"],
            )
        except Exception as e:
            messagebox.showerror(
                "Export Failed",
                f"Could not export: {e}",
                parent=self.winfo_toplevel(),
            )

    def _import(self):
        """Handle import."""
        filepath = filedialog.askopenfilename(
            title="Import Vault",
            filetypes=[("PassZen Vault", "*.passzen"), ("All Files", "*.*")],
            parent=self.winfo_toplevel(),
        )

        if not filepath:
            return

        # Ask for the source PIN
        from tkinter import simpledialog
        source_pin = simpledialog.askstring(
            "Source PIN",
            "Enter the PIN that was used when this file was exported:",
            show="●",
            parent=self.winfo_toplevel(),
        )

        if source_pin is None:
            return

        # Try to import
        entries, error = import_vault(filepath, source_pin)

        if error:
            messagebox.showerror(
                "Import Failed",
                error,
                parent=self.winfo_toplevel(),
            )
            return

        if not entries:
            self._status.configure(
                text="ℹ️  The file contained no entries.",
                fg=COLORS["text_secondary"],
            )
            return

        # Check for duplicates
        existing = self._db.get_all_entries()
        unique, duplicates = find_duplicates(existing, entries)

        # Import unique entries
        imported_count = 0
        for entry in unique:
            self._db.add_entry(entry)
            imported_count += 1

        # Report
        msg = f"✅ Imported {imported_count} new entries."
        if duplicates:
            msg += f"\n⚠️ Skipped {len(duplicates)} duplicates."

        self._status.configure(text=msg, fg=COLORS["success"])

        messagebox.showinfo(
            "Import Complete",
            msg,
            parent=self.winfo_toplevel(),
        )
