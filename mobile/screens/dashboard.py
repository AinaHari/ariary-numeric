import flet as ft

from mobile.components.common import *


def build_dashboard(page, state, navigate):
    user = state.get("user") or {}
    wallet_text = ft.Text("Solde : chargement...", size=18, weight=ft.FontWeight.BOLD)
    notif_count = ft.Text("")

    def refresh_wallet(e=None):
        r = state["api"].wallet()
        if r and r.status_code == 200:
            d = r.json()
            wallet_text.value = f"{d['balance']} {d['currency']} — Portefeuille de démonstration"
        else:
            wallet_text.value = "Solde indisponible"
        r2 = state["api"].notifications()
        if r2 and r2.status_code == 200:
            unread = [n for n in as_list(r2) if not n.get("is_read")]
            notif_count.value = f"Notifications : {len(unread)} non lues"
        page.update()

    refresh_wallet()

    def tile(icon, label, target):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=28, color=PRIMARY),
                    ft.Text(label, size=12, text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            on_click=lambda e, t=target: navigate(t),
            padding=8,
            bgcolor="#FFFFFF",
            border_radius=12,
            width=110,
            height=88,
            alignment=ft.Alignment.CENTER,
        )

    items = [
        tile(ft.Icons.SEND, "Envoyer", "transfer"),
        tile(ft.Icons.QR_CODE, "QR code", "qr"),
        tile(ft.Icons.HISTORY, "Historique", "history"),
        tile(ft.Icons.LOCAL_SHIPPING, "Expéditions", "shipments"),
        tile(ft.Icons.DESCRIPTION, "Douane", "customs"),
        tile(ft.Icons.CURRENCY_BITCOIN, "Blockchain", "blockchain"),
        tile(ft.Icons.PAYMENTS, "Paiements", "payments"),
        tile(ft.Icons.NOTIFICATIONS, "Notifications", "notifications"),
        tile(ft.Icons.PERSON, "Profil", "profile"),
    ]

    rows = []
    for i in range(0, len(items), 3):
        rows.append(
            ft.Row(items[i:i + 3], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
        )
    tiles = ft.Column(rows, spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    return ft.View(route="/dashboard",
        appbar=ft.AppBar(title=ft.Text("Tableau de bord", color="white"), bgcolor=PRIMARY,
                         actions=[ft.IconButton(ft.Icons.LOGOUT, on_click=lambda e: navigate("logout"), icon_color="white")]),
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(f"Bienvenue, {user.get('first_name') or user.get('email')}", size=16),
                        card(ft.Column([ft.Text("Portefeuille de démonstration — aucun argent réel", size=12, color="#C62828"),
                                        wallet_text, notif_count,
                                        ft.Row([button("Recharger démo", lambda e: navigate("topup"), primary=False)])])),
                        ft.Container(height=10),
                        tiles,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=16,
            )
        ],
    )
