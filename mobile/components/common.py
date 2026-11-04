import flet as ft
import os
import tempfile
import uuid

PRIMARY = "#1F3864"  # bleu nuit
ACCENT = "#2E7D32"  # vert
BG = "#F5F7FA"
CARD = "#FFFFFF"


def error_message(resp, default="Erreur réseau ou serveur."):
    """Extrait un message lisible d'une réponse HTTP (ou None)."""
    if resp is None:
        return "Serveur inaccessible."
    try:
        data = resp.json()
    except Exception:
        return default
    if isinstance(data, dict):
        if "detail" in data:
            return str(data["detail"])
        if "message" in data:
            return str(data["message"])
        parts = []
        for key, val in data.items():
            if isinstance(val, (list, tuple)):
                parts.append(f"{key}: {', '.join(str(v) for v in val)}")
            else:
                parts.append(f"{key}: {val}")
        if parts:
            return " | ".join(parts)
    if isinstance(data, list):
        return " | ".join(str(x) for x in data)
    return str(data) if data is not None else default

def snackbar(page, msg, error=False):
    """Affiche un message transitoire (Flet 1.x : page.show_dialog)."""
    sb = ft.SnackBar(
        ft.Text(msg, color="white"),
        bgcolor="#C62828" if error else ACCENT,
        duration=4000,
    )
    page.show_dialog(sb)

def card(content, padding=16):
    return ft.Container(
        content=content,
        padding=padding,
        bgcolor=CARD,
        border_radius=12,
        shadow=ft.BoxShadow(blur_radius=8, color="#1A000000"),
    )

def title(text):
    return ft.Text(text, size=20, weight=ft.FontWeight.BOLD, color=PRIMARY)

def button(label, on_click, icon=None, primary=True, width=None):
    """Bouton principal (≥ 48 px, accessible sur Android)."""
    return ft.FilledButton(
        content=label,
        icon=icon,
        on_click=on_click,
        height=48,
        style=ft.ButtonStyle(
            bgcolor=PRIMARY if primary else "#E8EDF5",
            color="white" if primary else PRIMARY,
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
        expand=width is None,
    )


def text_field(label, password=False, keyboard=None):
    return ft.TextField(
        label=label,
        password=password,
        can_reveal_password=password,
        keyboard_type=keyboard,
        border_radius=10,
    )


def tile(icon, label, target, navigate, width=96):
    """Tuile de navigation du tableau de bord."""
    return ft.Container(
        content=ft.Column(
            [
                ft.Icon(icon, size=28, color=PRIMARY),
                ft.Text(label, size=12, text_align=ft.TextAlign.CENTER),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        on_click=lambda e, t=target: navigate(t),
        padding=8,
        bgcolor=CARD,
        border_radius=12,
        width=width,
        height=88,
        alignment=ft.Alignment.CENTER,
    )


def back_bar(page, title_text, target="dashboard"):
    return app_bar(title_text, on_back=lambda e: page.navigate("/" + target))

def as_list(resp):
    """Extrait une liste d'items d'une réponse DRF (paginée ou non)."""
    if resp is None:
        return []
    try:
        data = resp.json()
    except Exception:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("results", []) or []
    return []

def app_bar(title_text, on_back=None):
    return ft.AppBar(
        title=ft.Text(title_text, color="white", weight=ft.FontWeight.BOLD),
        bgcolor=PRIMARY,
        leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=on_back, icon_color="white") if on_back else None,
    )
