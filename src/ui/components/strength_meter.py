"""
PassZen Strength Meter — Real-time password strength indicator widget.

Shows a colored progress bar and rating label that updates as the user types.
"""

import tkinter as tk
from tkinter import ttk

from src.ui.theme import COLORS, FONTS
from src.crypto.password_gen import calculate_strength


class StrengthMeter(ttk.Frame):
    """
    Visual password strength indicator.

    Displays a colored progress bar (Weak/Fair/Strong/Very Strong) and
    a text label. Updates in real-time via the `update(password)` method.
    """

    MAX_SCORE = 9

    def __init__(self, parent: tk.Widget, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)

        # Progress bar
        self._bar_frame = tk.Frame(self, bg=COLORS["bg"], height=8)
        self._bar_frame.pack(fill=tk.X, pady=(4, 2))

        self._bar_bg = tk.Frame(
            self._bar_frame, bg=COLORS["surface_light"], height=8
        )
        self._bar_bg.pack(fill=tk.X)

        self._bar_fill = tk.Frame(self._bar_bg, bg=COLORS["danger"], height=8)
        self._bar_fill.place(relx=0, rely=0, relwidth=0, relheight=1)

        # Label
        self._label = ttk.Label(
            self,
            text="",
            style="Caption.TLabel",
        )
        self._label.pack(anchor=tk.W, pady=(2, 0))

    def update(self, password: str):
        """
        Update the strength meter based on the given password.

        Args:
            password: The password to evaluate.
        """
        if not password:
            self._bar_fill.place(relwidth=0)
            self._label.configure(text="")
            return

        result = calculate_strength(password)
        score = result["score"]
        rating = result["rating"]
        color = result["color"]

        # Update bar width (proportional to score)
        width_fraction = score / self.MAX_SCORE
        self._bar_fill.configure(bg=color)
        self._bar_fill.place(relwidth=width_fraction)

        # Update label
        emoji_map = {
            "Weak": "🔴",
            "Fair": "🟡",
            "Strong": "🟢",
            "Very Strong": "🟣",
        }
        emoji = emoji_map.get(rating, "")
        self._label.configure(
            text=f"{emoji} {rating}",
            foreground=color,
        )
