import flet as ft

from mobile.components.common import *


def build_shipment_detail(page, state, navigate):
    ref = state.get("selected_shipment")
    info = ft.Text("Chargement...")
    events = ft.Column()
    new_status = ft.Dropdown(label="Nouveau statut", options=[
        ft.dropdown.Option("preparation", "Préparation"),
        ft.dropdown.Option("attente_depart", "En attente de départ"),
        ft.dropdown.Option("transit", "En transit"),
        ft.dropdown.Option("arrive_port", "Arrivé"),
        ft.dropdown.Option("dedouanement", "Dédouanement"),
        ft.dropdown.Option("libere", "Libéré"),
        ft.dropdown.Option("livraison", "En livraison"),
        ft.dropdown.Option("livre", "Livré"),
        ft.dropdown.Option("retarde", "Retardé"),
        ft.dropdown.Option("annule", "Annulé"),
    ])
    loc = text_field("Lieu")
    desc = text_field("Description")

    def refresh():
        r = state["api"].shipment_detail(ref)
        if r and r.status_code == 200:
            d = r.json()
            info.value = f"{d['reference']} — {d['name']}\n{d['origin']} → {d['destination']}\nStatut: {d['status']}\nMode: {d['mode']}\nTransporteur: {d.get('carrier')}\nSuivi: {d.get('tracking_number')}"
            events.controls.clear()
            for ev in d.get("events", []):
                events.controls.append(ft.Text(f"{ev['created_at'][:19]} — {ev['status']} — {ev.get('location','')} {ev.get('description','')}"))
        else:
            info.value = "Introuvable"
        page.update()

    def add_event(e):
        if not new_status.value:
            snackbar(page, "Statut requis.", error=True)
            return
        r = state["api"].add_shipment_event(ref, new_status.value, loc.value, desc.value)
        if r and r.status_code in (200, 201):
            snackbar(page, "Événement ajouté.")
            refresh()
        else:
            snackbar(page, "Erreur.", error=True)

    refresh()

    return ft.View(route="/shipmentdetail",
        appbar=ft.AppBar(title=ft.Text("Détail expédition", color="white"), bgcolor=PRIMARY,
                         leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate("shipments"), icon_color="white")),
        controls=[ft.Container(content=ft.Column([card(info), ft.Text("Chronologie", weight=ft.FontWeight.BOLD), events,
                                                 card(ft.Column([new_status, loc, desc, button("Ajouter événement", add_event)]))],
                                                scroll=ft.ScrollMode.AUTO), padding=16)],
    )
