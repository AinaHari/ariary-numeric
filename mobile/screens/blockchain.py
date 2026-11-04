import flet as ft

from mobile.components.common import *


def build_blockchain(page, state, navigate):
    info = ft.Text("Chargement...")
    records = ft.Column()
    record_type = text_field("Type d'enregistrement (ex: document)")
    payload = text_field("Données à empreinter")

    def refresh_info():
        r = state["api"].blockchain_info()
        if r and r.status_code == 200:
            d = r.json()
            info.value = f"Réseau: {d['network']} (chainId {d['chain_id']})\nRPC configuré: {d['rpc_configured']}\nStatut: {d['message']}"
        else:
            info.value = "Indisponible"
        page.update()

    def refresh_records():
        records.controls.clear()
        r = state["api"].blockchain_records()
        if r and r.status_code == 200:
            for rec in as_list(r):
                records.controls.append(ft.Text(f"{rec['id']} — {rec['record_type']} — {rec['data_hash'][:16]}… — {rec['status']}"))
        if not records.controls:
            records.controls.append(ft.Text("Aucun enregistrement."))
        page.update()

    def create_record(e):
        r = state["api"].create_blockchain_record(record_type.value or "document", payload.value or "")
        if r and r.status_code in (200, 201):
            d = r.json()
            snackbar(page, d.get("message", "Enregistré."))
            refresh_records()
        else:
            snackbar(page, "Erreur.", error=True)

    def verify(e):
        r = state["api"].blockchain_verify(payload=payload.value)
        if r and r.status_code == 200:
            d = r.json()
            snackbar(page, f"Vérifié: {d.get('verified')} (statut {d.get('status')})")
        else:
            snackbar(page, "Non trouvé.", error=True)

    refresh_info()
    refresh_records()

    return ft.View(route="/blockchain",
        appbar=ft.AppBar(title=ft.Text("Blockchain (test)", color="white"), bgcolor=PRIMARY,
                         leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate("dashboard"), icon_color="white")),
        controls=[ft.Container(content=ft.Column([card(info), ft.Text("Enregistrer une empreinte", weight=ft.FontWeight.BOLD),
                                                 record_type, payload,
                                                 ft.Row([button("Enregistrer", create_record), button("Vérifier", verify, primary=False)]),
                                                 ft.Text("Enregistrements", weight=ft.FontWeight.BOLD), records],
                                                scroll=ft.ScrollMode.AUTO), padding=16)],
    )
