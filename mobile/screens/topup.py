import flet as ft

from mobile.components.common import *


def build_topup(page, state, navigate):
    amount = text_field("Montant (MGA)", keyboard=ft.KeyboardType.NUMBER)

    def do_topup(e):
        try:
            val = float(amount.value)
        except Exception:
            snackbar(page, "Montant invalide.", error=True)
            return
        r = state["api"].topup_demo(val)
        if r and r.status_code in (200, 201):
            snackbar(page, "Rechargement démo effectué.")
            navigate("dashboard")
        else:
            snackbar(page, error_message(r), error=True)

    return ft.View(route="/topup",
        appbar=ft.AppBar(title=ft.Text("Recharger (démo)", color="white"), bgcolor=PRIMARY,
                         leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate("dashboard"), icon_color="white")),
        controls=[ft.Container(content=card(ft.Column([amount, button("Recharger", do_topup)])), padding=16)],
    )
