# modules/theme.py
import customtkinter as ctk

NAVY        = "#1e3a5f"
BLUE        = "#2563eb"
BLUE_DARK   = "#1d4ed8"
BLUE_LIGHT  = "#dbeafe"
BLUE_PALE   = "#eff6ff"
WHITE       = "#ffffff"
GRAY_50     = "#f8fafc"
GRAY_100    = "#f1f5f9"
GRAY_200    = "#e2e8f0"
GRAY_400    = "#94a3b8"
GRAY_600    = "#475569"
GRAY_800    = "#1e293b"
GRAY_900    = "#0f172a"
GREEN       = "#059669"
GREEN_LIGHT = "#d1fae5"
AMBER       = "#d97706"
AMBER_LIGHT = "#fef3c7"
RED         = "#dc2626"
RED_LIGHT   = "#fee2e2"

def FONT_HERO():    return ctk.CTkFont(family="Segoe UI", size=26, weight="bold")
def FONT_TITLE():   return ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
def FONT_HEADING(): return ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
def FONT_LABEL():   return ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
def FONT_BODY():    return ctk.CTkFont(family="Segoe UI", size=13)
def FONT_SMALL():   return ctk.CTkFont(family="Segoe UI", size=11)

def make_primary_btn(parent, text, command, width=120):
    return ctk.CTkButton(
        parent, text=text, width=width, height=36,
        fg_color=BLUE, hover_color=BLUE_DARK,
        font=FONT_LABEL(), corner_radius=8, command=command)

def make_entry(parent, placeholder, width=360, show=None):
    kwargs = dict(
        placeholder_text=placeholder, width=width,
        font=FONT_BODY(), height=38, corner_radius=8,
        border_color=GRAY_200, fg_color=WHITE, text_color=GRAY_900)
    if show:
        kwargs["show"] = show
    return ctk.CTkEntry(parent, **kwargs)

def make_dropdown(parent, values, width=360):
    return ctk.CTkComboBox(
        parent, values=values, width=width,
        font=FONT_BODY(), height=38, corner_radius=8,
        border_color=GRAY_200, fg_color=WHITE, text_color=GRAY_900,
        button_color=BLUE, button_hover_color=BLUE_DARK)

def make_delete_btn(parent, command):
    return ctk.CTkButton(
        parent, text="🗑️", width=36, height=28,
        fg_color=RED_LIGHT, hover_color=RED,
        text_color=RED, font=FONT_BODY(),
        corner_radius=6, command=command)

def make_stat_card(parent, label, value, icon, color, col):
    card = ctk.CTkFrame(
        parent, fg_color=WHITE, corner_radius=12,
        border_width=2, border_color=GRAY_200)
    card.grid(row=0, column=col, padx=8, pady=8, sticky="nsew")
    parent.grid_columnconfigure(col, weight=1)
    ctk.CTkFrame(card, fg_color=color, height=4,
                 corner_radius=0).pack(fill="x")
    ctk.CTkLabel(card, text=icon,
                 font=ctk.CTkFont(size=28)).pack(
        anchor="w", padx=16, pady=(12, 0))
    ctk.CTkLabel(card, text=value,
                 font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                 text_color=GRAY_900).pack(anchor="w", padx=16, pady=(4, 0))
    ctk.CTkLabel(card, text=label,
                 font=FONT_SMALL(),
                 text_color=GRAY_400).pack(anchor="w", padx=16, pady=(2, 14))
    return card

def make_table_header(parent, columns, widths):
    hr = ctk.CTkFrame(parent, fg_color=NAVY, height=40)
    hr.pack(fill="x", pady=(0, 2))
    hr.pack_propagate(False)
    for i, (col, w) in enumerate(zip(columns, widths)):
        ctk.CTkLabel(
            hr, text=col, font=FONT_SMALL(),
            text_color=WHITE, width=w, anchor="w").grid(
            row=0, column=i, padx=8, pady=8)
    return hr

def make_header_bar(parent, title, button_text=None, button_cmd=None):
    bar = ctk.CTkFrame(parent, fg_color=WHITE, height=64)
    bar.pack(fill="x")
    bar.pack_propagate(False)
    ctk.CTkLabel(
        bar, text=title, font=FONT_TITLE(),
        text_color=GRAY_900).pack(side="left", padx=24, pady=16)
    if button_text and button_cmd:
        make_primary_btn(
            bar, button_text, button_cmd).pack(
            side="right", padx=24, pady=14)
    return bar

def make_dialog(parent, title, width=440, height=520):
    dialog = ctk.CTkToplevel(parent)
    dialog.title(title)
    dialog.geometry(f"{width}x{height}")
    dialog.grab_set()
    dialog.resizable(False, False)
    hdr = ctk.CTkFrame(dialog, fg_color=NAVY, height=56)
    hdr.pack(fill="x")
    hdr.pack_propagate(False)
    ctk.CTkLabel(
        hdr, text=title, font=FONT_HEADING(),
        text_color=WHITE).pack(side="left", padx=20, pady=12)
    return dialog
def make_table_row(parent, values, widths, alt=False):
    bg = GRAY_50 if alt else WHITE
    row = ctk.CTkFrame(parent, fg_color=bg, corner_radius=0)
    row.pack(fill="x", pady=1)
    for i, (val, w) in enumerate(zip(values, widths)):
        ctk.CTkLabel(
            row, text=str(val), font=FONT_BODY(),
            text_color=GRAY_800, width=w, anchor="w").grid(
            row=0, column=i, padx=8, pady=6)
    return row