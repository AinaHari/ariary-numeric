import flet as ft

from mobile.components.common import *


def build_qrconfirm(page, state, navigate):
    to_email = state.get("scan_recipient", "")
    amount = text_field("Montant (MGA)", keyboard=ft.KeyboardType.NUMBER)

    def do_pay(e):
        try:
            val = float(amount.value)
        except Exception:
            snackbar(page, "Montant invalide.", error=True)
            return
        r = state["api"].transfer(to_email, val, "Paiement QR")
        if r and r.status_code in (200, 201):
            snackbar(page, "Paiement effectué.")
            navigate("wallet")
        else:
            snackbar(page, error_message(r), error=True)

    return ft.View(route="/qrconfirm",
        appbar=ft.AppBar(title=ft.Text("Confirmer le paiement", color="white"), bgcolor=PRIMARY,
                         leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate("qr"), icon_color="white")),
        controls=[
            ft.Container(content=card(ft.Column([
                ft.Text(f"Destinataire : {to_email}"),
                amount,
                ft.Text("Vérifiez le destinataire et le montant avant confirmation."),
                button("Confirmer", do_pay),
            ])), padding=16)
        ],
    )
