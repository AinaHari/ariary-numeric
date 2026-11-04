import flet as ft

from mobile.components.common import *


LABELS = {
    "reference": "Référence",
    "sender_email": "Expéditeur",
    "recipient_email": "Destinataire",
    "amount": "Montant",
    "fee": "Frais",
    "currency": "Devise",
    "kind": "Type",
    "status": "Statut",
    "description": "Description",
    "idempotency_key": "Clé d'idempotence",
    "created_at": "Créé le",
    "completed_at": "Terminé le",
}


def build_txdetail(page, state, navigate):
    ref = state.get("selected_tx")
    info = ft.Text("Chargement...")

    def refresh():
        r = state["api"].transaction_detail(ref)
        if r and r.status_code == 200:
            d = r.json()
            lines = []
            for k, v in d.items():
                label = LABELS.get(k, k)
                if v is None:
                    v = "—"
                lines.append(f"{label} : {v}")
            info.value = "\n".join(lines)
        else:
            info.value = error_message(r, "Transaction introuvable.")
        page.update()

    refresh()

    return ft.View(route="/txdetail",
        appbar=ft.AppBar(title=ft.Text("Détail transaction", color="white"), bgcolor=PRIMARY,
                         leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate("history"), icon_color="white")),
        controls=[ft.Container(content=card(info), padding=16)],
    )
