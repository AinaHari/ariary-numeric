import uuid

import flet as ft

from mobile.components.common import *


def build_transfer(page, state, navigate):
    recipient = text_field("E-mail du destinataire")
    amount = text_field("Montant (MGA)", keyboard=ft.KeyboardType.NUMBER)
    desc = text_field("Description (optionnel)")

    def do_transfer(e):
        try:
            val = float(amount.value)
        except Exception:
            snackbar(page, "Montant invalide.", error=True)
            return
        if not recipient.value:
            snackbar(page, "Destinataire requis.", error=True)
            return
        key = str(uuid.uuid4())
        r = state["api"].transfer(recipient.value.strip(), val, desc.value, idempotency_key=key)
        if r and r.status_code in (200, 201):
            snackbar(page, "Transfert effectué.")
            navigate("wallet")
        else:
            snackbar(page, error_message(r), error=True)

    return ft.View(route="/transfer",
        appbar=ft.AppBar(title=ft.Text("Envoyer", color="white"), bgcolor=PRIMARY,
                         leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate("dashboard"), icon_color="white")),
        controls=[
            ft.Container(content=card(ft.Column([recipient, amount, desc, button("Confirmer le transfert", do_transfer)])), padding=16)
        ],
    )
