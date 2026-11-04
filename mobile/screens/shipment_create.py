import flet as ft

from mobile.components.common import *


def build_shipment_create(page, state, navigate):
    name = text_field("Nom de la marchandise")
    origin = text_field("Origine")
    destination = text_field("Destination")
    mode = ft.Dropdown(label="Mode", options=[ft.dropdown.Option("maritime", "Maritime"), ft.dropdown.Option("aerien", "Aérien"), ft.dropdown.Option("terrestre", "Terrestre")], value="maritime")
    carrier = text_field("Transporteur")
    tracking = text_field("Numéro de suivi")

    def do_create(e):
        payload = {
            "name": name.value, "origin": origin.value, "destination": destination.value,
            "mode": mode.value, "carrier": carrier.value, "tracking_number": tracking.value,
        }
        r = state["api"].create_shipment(payload)
        if r and r.status_code in (200, 201):
            snackbar(page, "Expédition créée.")
            navigate("shipments")
        else:
            snackbar(page, error_message(r), error=True)

    return ft.View(route="/shipmentcreate",
        appbar=ft.AppBar(title=ft.Text("Nouvelle expédition", color="white"), bgcolor=PRIMARY,
                         leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate("shipments"), icon_color="white")),
        controls=[ft.Container(content=card(ft.Column([name, origin, destination, mode, carrier, tracking, button("Créer", do_create)])), padding=16)],
    )
