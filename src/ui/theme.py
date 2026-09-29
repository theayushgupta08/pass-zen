"""
PassZen Theme — Modern dark theme for Tkinter with custom styling.

Defines all colors, fonts, and ttk style configurations for the app.
Deep navy-black background, vibrant purple accent, teal-green secondary.
"""

import tkinter as tk
from tkinter import ttk
import platform


# ── Color Palette ────────────────────────────────────────────────────────────

COLORS = {
    "bg":              "#0F0F14",   # Deep navy-black
    "surface":         "#1A1A2E",   # Dark indigo (cards, panels)
    "surface_hover":   "#22223A",   # Slightly lighter hover state
    "surface_light":   "#252540",   # Lighter surface for inputs
    "primary":         "#6C63FF",   # Vibrant purple
    "primary_hover":   "#5A52E0",   # Darker purple on hover
    "primary_light":   "#8B85FF",   # Lighter purple
    "secondary":       "#00D4AA",   # Teal-green
    "secondary_hover": "#00B894",   # Darker teal on hover
    "text":            "#E8E8F0",   # Off-white primary text
    "text_secondary":  "#8888A0",   # Muted lavender secondary text
    "text_dim":        "#555570",   # Dimmed text
    "danger":          "#FF4757",   # Soft red
    "danger_hover":    "#E03E4D",   # Darker red on hover
    "success":         "#2ED573",   # Bright green
    "warning":         "#FFA502",   # Amber
    "border":          "#2A2A40",   # Subtle dark border
    "border_focus":    "#6C63FF",   # Purple border on focus
    "input_bg":        "#16162A",   # Input field background
    "scrollbar":       "#333350",   # Scrollbar track/thumb
}


# ── Fonts ────────────────────────────────────────────────────────────────────

def get_system_font() -> str:
    """Return the best system font for the current platform."""
    system = platform.system()
    if system == "Windows":
        return "Segoe UI"
    elif system == "Darwin":
        return "SF Pro Display"
    else:
        return "Ubuntu"  # Fallback for Linux


SYSTEM_FONT = get_system_font()

FONTS = {
    "heading_xl":    (SYSTEM_FONT, 28, "bold"),
    "heading_lg":    (SYSTEM_FONT, 22, "bold"),
    "heading":       (SYSTEM_FONT, 18, "bold"),
    "heading_sm":    (SYSTEM_FONT, 15, "bold"),
    "body":          (SYSTEM_FONT, 12),
    "body_bold":     (SYSTEM_FONT, 12, "bold"),
    "body_sm":       (SYSTEM_FONT, 11),
    "body_sm_bold":  (SYSTEM_FONT, 11, "bold"),
    "caption":       (SYSTEM_FONT, 10),
    "caption_bold":  (SYSTEM_FONT, 10, "bold"),
    "mono":          ("Consolas" if platform.system() == "Windows" else "Menlo", 12),
    "mono_lg":       ("Consolas" if platform.system() == "Windows" else "Menlo", 14),
    "pin":           (SYSTEM_FONT, 32, "bold"),
    "pin_dot":       (SYSTEM_FONT, 36, "bold"),
    "emoji":         ("Segoe UI Emoji" if platform.system() == "Windows" else SYSTEM_FONT, 16),
}


# ── Theme Application ───────────────────────────────────────────────────────

def apply_theme(root: tk.Tk):
    """
    Apply the PassZen dark theme to a Tkinter root window.

    Configures the root window appearance and all ttk widget styles.

    Args:
        root: The Tkinter root window.
    """
    # Root window config
    root.configure(bg=COLORS["bg"])
    root.option_add("*Font", FONTS["body"])
    root.option_add("*Background", COLORS["bg"])
    root.option_add("*Foreground", COLORS["text"])

    # Use 'clam' as the base theme (most customizable)
    style = ttk.Style(root)
    style.theme_use("clam")

    # ── Global ttk styles ────────────────────────────────────────────

    # Frame
    style.configure(
        "TFrame",
        background=COLORS["bg"],
    )
    style.configure(
        "Surface.TFrame",
        background=COLORS["surface"],
    )
    style.configure(
        "Card.TFrame",
        background=COLORS["surface"],
    )

    # Label
    style.configure(
        "TLabel",
        background=COLORS["bg"],
        foreground=COLORS["text"],
        font=FONTS["body"],
    )
    style.configure(
        "Heading.TLabel",
        font=FONTS["heading"],
        foreground=COLORS["text"],
    )
    style.configure(
        "HeadingXL.TLabel",
        font=FONTS["heading_xl"],
        foreground=COLORS["text"],
    )
    style.configure(
        "HeadingSm.TLabel",
        font=FONTS["heading_sm"],
        foreground=COLORS["text"],
    )
    style.configure(
        "Secondary.TLabel",
        foreground=COLORS["text_secondary"],
        font=FONTS["body_sm"],
    )
    style.configure(
        "Caption.TLabel",
        foreground=COLORS["text_dim"],
        font=FONTS["caption"],
    )
    style.configure(
        "Primary.TLabel",
        foreground=COLORS["primary"],
    )
    style.configure(
        "Success.TLabel",
        foreground=COLORS["success"],
    )
    style.configure(
        "Danger.TLabel",
        foreground=COLORS["danger"],
    )
    style.configure(
        "Warning.TLabel",
        foreground=COLORS["warning"],
    )
    style.configure(
        "Surface.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["text"],
    )
    style.configure(
        "SurfaceSecondary.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["text_secondary"],
        font=FONTS["body_sm"],
    )
    style.configure(
        "SurfaceCaption.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["text_dim"],
        font=FONTS["caption"],
    )

    # Button — Primary
    style.configure(
        "Primary.TButton",
        background=COLORS["primary"],
        foreground="#FFFFFF",
        font=FONTS["body_bold"],
        borderwidth=0,
        padding=(20, 10),
        focuscolor=COLORS["primary"],
    )
    style.map(
        "Primary.TButton",
        background=[
            ("active", COLORS["primary_hover"]),
            ("disabled", COLORS["surface_light"]),
        ],
        foreground=[("disabled", COLORS["text_dim"])],
    )

    # Button — Secondary
    style.configure(
        "Secondary.TButton",
        background=COLORS["surface_light"],
        foreground=COLORS["text"],
        font=FONTS["body"],
        borderwidth=0,
        padding=(16, 8),
        focuscolor=COLORS["surface_light"],
    )
    style.map(
        "Secondary.TButton",
        background=[("active", COLORS["surface_hover"])],
    )

    # Button — Danger
    style.configure(
        "Danger.TButton",
        background=COLORS["danger"],
        foreground="#FFFFFF",
        font=FONTS["body_bold"],
        borderwidth=0,
        padding=(16, 8),
        focuscolor=COLORS["danger"],
    )
    style.map(
        "Danger.TButton",
        background=[("active", COLORS["danger_hover"])],
    )

    # Button — Ghost (transparent)
    style.configure(
        "Ghost.TButton",
        background=COLORS["bg"],
        foreground=COLORS["text_secondary"],
        font=FONTS["body_sm"],
        borderwidth=0,
        padding=(8, 4),
        focuscolor=COLORS["bg"],
    )
    style.map(
        "Ghost.TButton",
        background=[("active", COLORS["surface"])],
        foreground=[("active", COLORS["text"])],
    )

    # Button — Icon-like small button
    style.configure(
        "Icon.TButton",
        background=COLORS["surface"],
        foreground=COLORS["text_secondary"],
        font=FONTS["body"],
        borderwidth=0,
        padding=(8, 4),
        focuscolor=COLORS["surface"],
    )
    style.map(
        "Icon.TButton",
        background=[("active", COLORS["surface_hover"])],
        foreground=[("active", COLORS["primary"])],
    )

    # Entry
    style.configure(
        "TEntry",
        fieldbackground=COLORS["input_bg"],
        foreground=COLORS["text"],
        insertcolor=COLORS["text"],
        borderwidth=1,
        padding=(10, 8),
    )
    style.map(
        "TEntry",
        fieldbackground=[("focus", COLORS["surface_light"])],
        bordercolor=[
            ("focus", COLORS["border_focus"]),
            ("!focus", COLORS["border"]),
        ],
    )

    # Combobox
    style.configure(
        "TCombobox",
        fieldbackground=COLORS["input_bg"],
        background=COLORS["surface_light"],
        foreground=COLORS["text"],
        arrowcolor=COLORS["text_secondary"],
        borderwidth=1,
        padding=(10, 8),
    )
    style.map(
        "TCombobox",
        fieldbackground=[("focus", COLORS["surface_light"])],
        bordercolor=[
            ("focus", COLORS["border_focus"]),
            ("!focus", COLORS["border"]),
        ],
    )

    # Checkbutton
    style.configure(
        "TCheckbutton",
        background=COLORS["bg"],
        foreground=COLORS["text"],
        font=FONTS["body"],
        focuscolor=COLORS["bg"],
    )
    style.map(
        "TCheckbutton",
        background=[("active", COLORS["bg"])],
    )
    style.configure(
        "Surface.TCheckbutton",
        background=COLORS["surface"],
        focuscolor=COLORS["surface"],
    )
    style.map(
        "Surface.TCheckbutton",
        background=[("active", COLORS["surface"])],
    )

    # Scale (slider)
    style.configure(
        "TScale",
        background=COLORS["bg"],
        troughcolor=COLORS["surface_light"],
        sliderthickness=20,
    )

    # Separator
    style.configure(
        "TSeparator",
        background=COLORS["border"],
    )

    # Scrollbar
    style.configure(
        "Vertical.TScrollbar",
        background=COLORS["scrollbar"],
        troughcolor=COLORS["bg"],
        borderwidth=0,
        arrowsize=0,
    )
    style.map(
        "Vertical.TScrollbar",
        background=[("active", COLORS["text_dim"])],
    )

    # Notebook (tabs)
    style.configure(
        "TNotebook",
        background=COLORS["bg"],
        borderwidth=0,
    )
    style.configure(
        "TNotebook.Tab",
        background=COLORS["surface"],
        foreground=COLORS["text_secondary"],
        font=FONTS["body_sm"],
        padding=(16, 8),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", COLORS["primary"])],
        foreground=[("selected", "#FFFFFF")],
    )

    # Progressbar (used for strength meter)
    style.configure(
        "Strength.Horizontal.TProgressbar",
        background=COLORS["primary"],
        troughcolor=COLORS["surface_light"],
        borderwidth=0,
        thickness=8,
    )

    # PIN-specific styles
    style.configure(
        "PIN.TButton",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        font=FONTS["pin"],
        borderwidth=0,
        padding=(0, 12),
        focuscolor=COLORS["surface"],
    )
    style.map(
        "PIN.TButton",
        background=[("active", COLORS["surface_hover"])],
        foreground=[("active", COLORS["primary"])],
    )

    # Tab filter buttons
    style.configure(
        "Filter.TButton",
        background=COLORS["surface"],
        foreground=COLORS["text_secondary"],
        font=FONTS["body_sm"],
        borderwidth=0,
        padding=(12, 6),
        focuscolor=COLORS["surface"],
    )
    style.map(
        "Filter.TButton",
        background=[("active", COLORS["surface_hover"])],
        foreground=[("active", COLORS["text"])],
    )

    style.configure(
        "FilterActive.TButton",
        background=COLORS["primary"],
        foreground="#FFFFFF",
        font=FONTS["body_sm_bold"],
        borderwidth=0,
        padding=(12, 6),
        focuscolor=COLORS["primary"],
    )
    style.map(
        "FilterActive.TButton",
        background=[("active", COLORS["primary_hover"])],
    )
