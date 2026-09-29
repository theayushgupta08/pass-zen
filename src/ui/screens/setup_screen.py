"""
PassZen Setup Screen — First-time PIN creation and recovery setup.

Shown when no vault exists. Guides the user through:
1. Create a 6-digit PIN
2. Confirm the PIN
3. Set a security question and answer
4. Display the one-time recovery key
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from src.ui.theme import COLORS, FONTS
from src.ui.components.pin_pad import PinPad


# Security questions the user can choose from
SECURITY_QUESTIONS = [
    "What was the name of your first pet?",
    "What city were you born in?",
    "What is your mother's maiden name?",
    "What was the name of your first school?",
    "What is your favorite movie?",
    "What was your childhood nickname?",
    "What street did you grow up on?",
    "What is the name of your best friend from childhood?",
]


class SetupScreen(ttk.Frame):
    """
    First-time setup flow: PIN creation → PIN confirmation → Security Q&A
    → Recovery key display.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_complete: Callable,
        vault,
        **kwargs,
    ):
        super().__init__(parent, style="TFrame", **kwargs)
        self._parent = parent
        self._on_complete = on_complete
        self._vault = vault
        self._pin = ""
        self._step = 1  # 1=create, 2=confirm, 3=security, 4=recovery key

        self._show_step_1()

    def _clear(self):
        """Clear all widgets from this frame."""
        for widget in self.winfo_children():
            widget.destroy()

    # ── Step 1: Create PIN ───────────────────────────────────────────

    def _show_step_1(self):
        """Show the PIN creation screen."""
        self._clear()

        # Center container
        container = ttk.Frame(self, style="TFrame")
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Logo/Title
        title = ttk.Label(
            container,
            text="🔐 Welcome to PassZen",
            style="HeadingXL.TLabel",
        )
        title.pack(pady=(0, 8))

        subtitle = ttk.Label(
            container,
            text="Create a 6-digit PIN to secure your vault",
            style="Secondary.TLabel",
        )
        subtitle.pack(pady=(0, 40))

        # Step indicator
        step_label = ttk.Label(
            container,
            text="Step 1 of 3 — Create PIN",
            style="Primary.TLabel",
            font=FONTS["body_sm_bold"],
        )
        step_label.pack(pady=(0, 20))

        # PIN pad
        self._pin_pad = PinPad(
            container,
            on_complete=self._on_pin_created,
        )
        self._pin_pad.pack()

    def _on_pin_created(self, pin: str):
        """Handle PIN creation."""
        self._pin = pin
        self._step = 2
        self._show_step_2()

    # ── Step 2: Confirm PIN ──────────────────────────────────────────

    def _show_step_2(self):
        """Show the PIN confirmation screen."""
        self._clear()

        container = ttk.Frame(self, style="TFrame")
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        title = ttk.Label(
            container,
            text="🔐 Confirm Your PIN",
            style="HeadingXL.TLabel",
        )
        title.pack(pady=(0, 8))

        subtitle = ttk.Label(
            container,
            text="Enter the same PIN again to confirm",
            style="Secondary.TLabel",
        )
        subtitle.pack(pady=(0, 40))

        step_label = ttk.Label(
            container,
            text="Step 1 of 3 — Confirm PIN",
            style="Primary.TLabel",
            font=FONTS["body_sm_bold"],
        )
        step_label.pack(pady=(0, 20))

        self._pin_pad = PinPad(
            container,
            on_complete=self._on_pin_confirmed,
        )
        self._pin_pad.pack()

        # Back button
        back_btn = ttk.Button(
            container,
            text="← Back",
            style="Ghost.TButton",
            command=self._show_step_1,
        )
        back_btn.pack(pady=(20, 0))

    def _on_pin_confirmed(self, pin: str):
        """Handle PIN confirmation."""
        if pin != self._pin:
            messagebox.showerror(
                "PIN Mismatch",
                "The PINs don't match. Please try again.",
                parent=self.winfo_toplevel(),
            )
            self._pin_pad.clear()
            return

        self._step = 3
        self._show_step_3()

    # ── Step 3: Security Question ────────────────────────────────────

    def _show_step_3(self):
        """Show the security question setup screen."""
        self._clear()

        container = ttk.Frame(self, style="TFrame")
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        title = ttk.Label(
            container,
            text="🛡️ Recovery Setup",
            style="HeadingXL.TLabel",
        )
        title.pack(pady=(0, 8))

        subtitle = ttk.Label(
            container,
            text="Set up recovery in case you forget your PIN",
            style="Secondary.TLabel",
        )
        subtitle.pack(pady=(0, 30))

        step_label = ttk.Label(
            container,
            text="Step 2 of 3 — Security Question",
            style="Primary.TLabel",
            font=FONTS["body_sm_bold"],
        )
        step_label.pack(pady=(0, 20))

        # Form
        form = ttk.Frame(container, style="TFrame")
        form.pack(fill=tk.X, padx=40)

        # Security question dropdown
        q_label = ttk.Label(
            form, text="Security Question", style="TLabel",
            font=FONTS["body_sm_bold"],
        )
        q_label.pack(anchor=tk.W, pady=(0, 4))

        self._question_var = tk.StringVar(value=SECURITY_QUESTIONS[0])
        q_combo = ttk.Combobox(
            form,
            textvariable=self._question_var,
            values=SECURITY_QUESTIONS,
            state="readonly",
            style="TCombobox",
            font=FONTS["body"],
            width=45,
        )
        q_combo.pack(fill=tk.X, pady=(0, 16))

        # Security answer
        a_label = ttk.Label(
            form, text="Your Answer", style="TLabel",
            font=FONTS["body_sm_bold"],
        )
        a_label.pack(anchor=tk.W, pady=(0, 4))

        self._answer_var = tk.StringVar()
        a_entry = tk.Entry(
            form,
            textvariable=self._answer_var,
            font=FONTS["body"],
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"],
        )
        a_entry.pack(fill=tk.X, ipady=10, pady=(0, 24))

        # Continue button
        continue_btn = ttk.Button(
            form,
            text="Continue →",
            style="Primary.TButton",
            command=self._on_security_submitted,
        )
        continue_btn.pack(fill=tk.X)

        # Back button
        back_btn = ttk.Button(
            form,
            text="← Back",
            style="Ghost.TButton",
            command=self._show_step_1,
        )
        back_btn.pack(pady=(12, 0))

    def _on_security_submitted(self):
        """Handle security question submission."""
        answer = self._answer_var.get().strip()
        if not answer:
            messagebox.showwarning(
                "Answer Required",
                "Please enter an answer to the security question.",
                parent=self.winfo_toplevel(),
            )
            return

        # Initialize the vault
        question = self._question_var.get()
        recovery_key = self._vault.initialize(self._pin, question, answer)
        self._recovery_key = recovery_key

        self._step = 4
        self._show_step_4()

    # ── Step 4: Recovery Key Display ─────────────────────────────────

    def _show_step_4(self):
        """Show the recovery key for the user to save."""
        self._clear()

        container = ttk.Frame(self, style="TFrame")
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        title = ttk.Label(
            container,
            text="🔑 Your Recovery Key",
            style="HeadingXL.TLabel",
        )
        title.pack(pady=(0, 8))

        subtitle = ttk.Label(
            container,
            text="Save this key in a safe place. You'll need it if you forget your PIN.",
            style="Secondary.TLabel",
        )
        subtitle.pack(pady=(0, 30))

        step_label = ttk.Label(
            container,
            text="Step 3 of 3 — Save Recovery Key",
            style="Primary.TLabel",
            font=FONTS["body_sm_bold"],
        )
        step_label.pack(pady=(0, 20))

        # Recovery key display
        key_frame = tk.Frame(
            container,
            bg=COLORS["surface"],
            highlightthickness=1,
            highlightbackground=COLORS["primary"],
            padx=24,
            pady=16,
        )
        key_frame.pack(pady=(0, 8))

        key_label = tk.Label(
            key_frame,
            text=self._recovery_key,
            font=FONTS["mono_lg"],
            bg=COLORS["surface"],
            fg=COLORS["secondary"],
        )
        key_label.pack()

        # Copy button
        def copy_key():
            self.winfo_toplevel().clipboard_clear()
            self.winfo_toplevel().clipboard_append(self._recovery_key)
            copied_label.configure(text="✅ Copied!")
            self.after(2000, lambda: copied_label.configure(text=""))

        copy_btn = ttk.Button(
            container,
            text="📋 Copy to Clipboard",
            style="Secondary.TButton",
            command=copy_key,
        )
        copy_btn.pack(pady=(8, 4))

        copied_label = ttk.Label(
            container, text="", style="Success.TLabel",
        )
        copied_label.pack(pady=(0, 16))

        # Warning
        warning_frame = tk.Frame(container, bg=COLORS["surface"], padx=16, pady=12)
        warning_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        warning_text = tk.Label(
            warning_frame,
            text="⚠️  This key will NOT be shown again. If you lose it and\n"
                 "forget your PIN, your vault cannot be recovered.",
            font=FONTS["body_sm"],
            bg=COLORS["surface"],
            fg=COLORS["warning"],
            justify=tk.LEFT,
        )
        warning_text.pack()

        # Checkbox: I've saved my recovery key
        self._saved_var = tk.BooleanVar(value=False)
        saved_check = ttk.Checkbutton(
            container,
            text="  I've saved my recovery key",
            variable=self._saved_var,
            style="TCheckbutton",
            command=self._toggle_finish_button,
        )
        saved_check.pack(pady=(0, 16))

        # Finish button (disabled until checkbox is checked)
        self._finish_btn = ttk.Button(
            container,
            text="🚀 Open PassZen",
            style="Primary.TButton",
            command=self._finish_setup,
            state="disabled",
        )
        self._finish_btn.pack()

    def _toggle_finish_button(self):
        """Enable/disable finish button based on checkbox."""
        if self._saved_var.get():
            self._finish_btn.configure(state="normal")
        else:
            self._finish_btn.configure(state="disabled")

    def _finish_setup(self):
        """Complete setup and transition to dashboard."""
        self._on_complete()
